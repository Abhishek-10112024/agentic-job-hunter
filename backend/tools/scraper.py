import requests


COMPANIES = [
    "openai",
    "huggingface",
    "scaleai",
    "anthropic",
    "databricks"
]


def scrape_jobs():
    jobs = []

    for company in COMPANIES:
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

        try:
            response = requests.get(api_url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                for job in data.get("jobs", []):
                    jobs.append({
                        "company": company,
                        "title": job.get("title"),
                        "link": job.get("absolute_url"),
                        "location": job.get("location", {}).get("name")
                    })

        except:
            continue

    return jobs[:20]