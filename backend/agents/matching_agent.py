from chromadb.utils import embedding_functions
import numpy as np

embedding_function = embedding_functions.DefaultEmbeddingFunction()


def compute_similarity(resume_text: str, jobs: list):
    results = []

    # Embed resume
    resume_embedding = embedding_function([resume_text])[0]

    for job in jobs:
        job_text = f"""
        Title: {job.get("title", "")}
        Company: {job.get("company", "")}
        Location: {job.get("location", "")}
        """

        job_embedding = embedding_function([job_text])[0]

        # 🔥 Cosine similarity
        similarity = np.dot(resume_embedding, job_embedding) / (
            np.linalg.norm(resume_embedding) * np.linalg.norm(job_embedding)
        )

        title = job.get("title", "").lower()

        # 🔥 1. Role-based adjustment
        role_adjustment = 0

        if any(word in title for word in ["engineer", "developer"]):
            role_adjustment += 0.1

        if any(word in title for word in ["manager", "consultant", "strategy"]):
            role_adjustment -= 0.1

        # 🔥 2. Keyword alignment boost
        keyword_boost = 0

        keywords = ["ai", "ml", "machine learning", "llm", "data", "genai"]

        for keyword in keywords:
            if keyword in title:
                keyword_boost += 0.02

        # 🔥 Final score
        final_score = similarity + role_adjustment + keyword_boost

        results.append({
            **job,
            "score": float(final_score)
        })

    # Sort by score
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results