import logging
import os
import shutil

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root before importing any agent modules
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

from app.config import CORS_ORIGINS                  # noqa: E402
from utils.resume_parser import extract_text_from_pdf  # noqa: E402
from agents.resume_agent import extract_resume_info    # noqa: E402
from memory.vector_store import store_resume           # noqa: E402
from tools.scraper import scrape_jobs                  # noqa: E402
from agents.matching_agent import compute_similarity   # noqa: E402
from agents.explanation_agent import explain_match     # noqa: E402
from agents.skill_gap_agent import analyze_skill_gap   # noqa: E402

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="Agentic Job Hunter", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,   # explicit local origins only
    allow_credentials=False,      # False when origins are explicit (avoids wildcard conflict)
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Accept"],
)

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# In-process session state (single-user local tool — no auth required)
# ---------------------------------------------------------------------------
_session: dict = {
    "resume_text": "",
    "structured_data": {},
}

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Quick liveness probe."""
    return {"status": "ok"}


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    logger.info("Resume uploaded: %s", file.filename)

    extracted_text = extract_text_from_pdf(str(file_path))
    if not extracted_text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from the PDF. Is it scanned?")

    _session["resume_text"] = extracted_text[:4000]
    _session["structured_data"] = extract_resume_info(_session["resume_text"])

    store_resume(file.filename, _session["resume_text"])

    return {
        "message": "Resume processed & stored successfully",
        "structured_data": _session["structured_data"],
    }


@app.get("/scrape-jobs")
def get_jobs():
    if not _session["resume_text"]:
        raise HTTPException(status_code=400, detail="Please upload a resume first.")

    raw_jobs = scrape_jobs()
    logger.info("Scraped %d raw jobs", len(raw_jobs))

    # Filter to relevant tech roles
    relevant_keywords = {"engineer", "developer", "machine learning", "ai", "data", "scientist", "analyst"}
    filtered_jobs = [
        job for job in raw_jobs
        if any(kw in (job.get("title") or "").lower() for kw in relevant_keywords)
    ]
    logger.info("Filtered to %d relevant jobs", len(filtered_jobs))

    if not filtered_jobs:
        return {"jobs": [], "message": "No relevant jobs found from the job boards right now."}

    ranked_jobs = compute_similarity(_session["resume_text"], filtered_jobs)

    # Only jobs with a meaningful similarity score
    ranked_jobs = [job for job in ranked_jobs if job["score"] > 0.3]

    resume_skills = _session["structured_data"].get("skills", [])
    skills_text = ", ".join(resume_skills)

    # Enrich top-5 with AI explanations
    for job in ranked_jobs[:5]:
        try:
            job["why_match"] = explain_match(_session["resume_text"], job)
        except Exception:
            logger.exception("explain_match failed for: %s", job.get("title"))
            job["why_match"] = "Explanation unavailable."

        try:
            job["skill_gap"] = analyze_skill_gap(skills_text, job)
        except Exception:
            logger.exception("analyze_skill_gap failed for: %s", job.get("title"))
            job["skill_gap"] = {"missing_skills": []}

        job["match_score"] = round(job["score"] * 100, 2)

    # Remaining jobs (beyond top-5) still get a score, just no AI text
    for job in ranked_jobs[5:]:
        job["match_score"] = round(job["score"] * 100, 2)
        job.setdefault("why_match", "")
        job.setdefault("skill_gap", {"missing_skills": []})

    return {"jobs": ranked_jobs[:10]}
