import json
import re
import time
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.config import GOOGLE_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_RETRY_DELAY = 5


def _make_llm():
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0,
        google_api_key=GOOGLE_API_KEY,
    )


def extract_resume_info(resume_text: str) -> dict:
    """Extract structured skills, experience, roles and domains from resume text."""
    prompt = PromptTemplate(
        input_variables=["resume"],
        template=(
            "Extract structured information from the following resume.\n\n"
            "Resume:\n{resume}\n\n"
            "Return ONLY valid JSON (no explanation, no markdown fences):\n"
            '{{\n'
            '    "skills": [],\n'
            '    "experience": [],\n'
            '    "roles": [],\n'
            '    "domains": []\n'
            '}}'
        ),
    )

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            chain = prompt | _make_llm()
            response = chain.invoke({"resume": resume_text})
            raw_output = response.content
            cleaned_output = re.sub(r"```(?:json)?", "", raw_output).strip()
            return json.loads(cleaned_output)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from resume agent (attempt %d)", attempt)
            return {"error": "Failed to parse JSON", "raw": raw_output[:200]}
        except Exception as e:
            if "503" in str(e) and attempt < _MAX_RETRIES:
                logger.warning("extract_resume_info: 503 on attempt %d, retrying in %ds…", attempt, _RETRY_DELAY)
                time.sleep(_RETRY_DELAY)
            else:
                logger.exception("extract_resume_info failed")
                return {"skills": [], "experience": [], "roles": [], "domains": []}