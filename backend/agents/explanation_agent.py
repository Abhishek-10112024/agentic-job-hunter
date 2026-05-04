import os
import time
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.config import GOOGLE_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_RETRY_DELAY = 5  # seconds between retries on 503


def _make_llm():
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0,
        google_api_key=GOOGLE_API_KEY,
    )


def explain_match(resume_text: str, job: dict) -> str:
    """Generate a 2-line explanation of why this job matches the candidate."""
    prompt = PromptTemplate(
        input_variables=["resume", "job"],
        template=(
            "Resume:\n{resume}\n\n"
            "Job Title: {job}\n\n"
            "Explain in exactly 2 sentences why this job is a strong match "
            "for the candidate based on their resume. Be specific."
        ),
    )

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            chain = prompt | _make_llm()
            response = chain.invoke({"resume": resume_text, "job": job["title"]})
            return response.content.strip()
        except Exception as e:
            if "503" in str(e) and attempt < _MAX_RETRIES:
                logger.warning("explain_match: 503 on attempt %d, retrying in %ds…", attempt, _RETRY_DELAY)
                time.sleep(_RETRY_DELAY)
            else:
                logger.exception("explain_match failed for job: %s", job.get("title"))
                return "Explanation unavailable."