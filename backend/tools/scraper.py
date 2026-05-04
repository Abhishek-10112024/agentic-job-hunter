import json
import logging
from pathlib import Path
import requests

logger = logging.getLogger(__name__)

_COMPANIES_FILE = Path(__file__).resolve().parents[1] / "config" / "companies.json"


def _load_companies() -> list[str]:
    """Load Greenhouse board slugs from config/companies.json."""
    try:
        with open(_COMPANIES_FILE) as f:
            return json.load(f).get("companies", [])
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        logger.warning("Could not load companies.json: %s — using defaults.", exc)
        return ["openai", "anthropic", "huggingface"]


def scrape_jobs(max_per_company: int = 10) -> list[dict]:
    """Fetch live job listings from Greenhouse public job board API."""
    companies = _load_companies()
    jobs: list[dict] = []

    for company in companies:
        url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            for job in data.get("jobs", [])[:max_per_company]:
                jobs.append({
                    "company": company,
                    "title": job.get("title", "").strip(),
                    "link": job.get("absolute_url", ""),
                    "location": (job.get("location") or {}).get("name", "Remote/Unspecified"),
                })

            logger.info("Fetched %d jobs from %s", len(data.get("jobs", [])), company)

        except requests.exceptions.RequestException as exc:
            logger.warning("Could not fetch jobs for %s: %s", company, exc)

    logger.info("Total jobs fetched: %d", len(jobs))
    return jobs