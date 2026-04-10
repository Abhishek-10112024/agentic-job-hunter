USER_RESUME_TEXT = ""
USER_STRUCTURED_DATA = {}

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

from utils.resume_parser import extract_text_from_pdf
from agents.resume_agent import extract_resume_info
from memory.vector_store import store_resume
from tools.scraper import scrape_jobs
from agents.matching_agent import compute_similarity
from agents.explanation_agent import explain_match
from agents.skill_gap_agent import analyze_skill_gap

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (for dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    global USER_RESUME_TEXT, USER_STRUCTURED_DATA

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text_from_pdf(file_path)

    USER_RESUME_TEXT = extracted_text[:3000]

    structured_data = extract_resume_info(USER_RESUME_TEXT)
    USER_STRUCTURED_DATA = structured_data

    store_resume(file.filename, USER_RESUME_TEXT)

    return {
        "message": "Resume processed & stored successfully",
        "structured_data": structured_data
    }


@app.get("/scrape-jobs")
def get_jobs():
    jobs = scrape_jobs()

    global USER_RESUME_TEXT, USER_STRUCTURED_DATA

    if not USER_RESUME_TEXT:
        return {"error": "Please upload resume first"}

    # 🔥 FILTER IRRELEVANT ROLES FIRST
    filtered_jobs = [
        job for job in jobs
        if any(keyword in job["title"].lower() for keyword in [
            "engineer", "developer", "machine learning", "ai", "data"
        ])
    ]

    ranked_jobs = compute_similarity(USER_RESUME_TEXT, filtered_jobs)

    ranked_jobs = [job for job in ranked_jobs if job["score"] > 0.3]

    # 🔥 Extract structured skills
    resume_skills = USER_STRUCTURED_DATA.get("skills", [])

    # 🔥 ADD EXPLANATION + SKILL GAP
    for job in ranked_jobs[:5]:
        try:
            job["why_match"] = explain_match(USER_RESUME_TEXT, job)

            job["skill_gap"] = analyze_skill_gap(
                ", ".join(resume_skills),
                job
            )

            # 🔥 Bonus: readable score
            job["match_score"] = round(job["score"] * 100, 2)

        except:
            job["why_match"] = "Could not generate explanation"
            job["skill_gap"] = {"missing_skills": []}
            job["match_score"] = round(job["score"] * 100, 2)

    return {
        "jobs": ranked_jobs[:10]
    }
