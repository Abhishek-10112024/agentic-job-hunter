import json
import time
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.config import GOOGLE_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_RETRY_DELAY = 5

ADVANCED_SKILLS = [
    "Kubernetes",
    "Distributed Systems",
    "System Design",
    "Terraform",
    "Model Monitoring",
    "Data Pipelines",
    "Scalable ML Systems",
]


def _make_llm():
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0,
        google_api_key=GOOGLE_API_KEY,
    )


def analyze_skill_gap(resume_skills: str, job: dict) -> dict:
    """Identify advanced/production-level skills required for the job that are missing from the resume."""
    prompt = PromptTemplate(
        input_variables=["resume", "job"],
        template=(
            "Resume Skills:\n{resume}\n\n"
            "Job Title: {job}\n\n"
            "Task:\n"
            "- Identify ADVANCED or PRODUCTION-LEVEL skills required for this job.\n"
            "- Compare with resume skills.\n"
            "- Return ONLY skills that are NOT clearly present in the resume.\n\n"
            "Rules:\n"
            "- Do NOT repeat resume skills.\n"
            "- Focus on real industry gaps, not basic tools.\n"
            "- Return max 3-5 skills.\n\n"
            "Return ONLY valid JSON (no markdown):\n"
            '{{\n    "missing_skills": []\n}}'
        ),
    )

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            chain = prompt | _make_llm()
            response = chain.invoke({"resume": resume_skills, "job": job["title"]})
            cleaned = response.content.replace("```json", "").replace("```", "").strip()
            result = json.loads(cleaned)
            if not result.get("missing_skills"):
                result["missing_skills"] = ADVANCED_SKILLS[:3]
            return result
        except Exception as e:
            if "503" in str(e) and attempt < _MAX_RETRIES:
                logger.warning("analyze_skill_gap: 503 on attempt %d, retrying in %ds…", attempt, _RETRY_DELAY)
                time.sleep(_RETRY_DELAY)
            else:
                logger.exception("analyze_skill_gap failed for job: %s", job.get("title"))
                return {"missing_skills": ADVANCED_SKILLS[:3]}