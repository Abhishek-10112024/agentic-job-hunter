import logging
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)

# Persist to disk so the index survives server restarts
_PERSIST_DIR = Path(__file__).resolve().parents[2] / ".chroma_db"
_PERSIST_DIR.mkdir(exist_ok=True)

client = chromadb.PersistentClient(path=str(_PERSIST_DIR))

embedding_function = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="resume_collection",
    embedding_function=embedding_function,
)


def store_resume(resume_id: str, resume_text: str) -> None:
    """Upsert a resume so re-uploads don't throw a duplicate-ID error."""
    try:
        collection.upsert(
            documents=[resume_text],
            ids=[resume_id],
        )
        logger.info("Stored/updated resume: %s", resume_id)
    except Exception:
        logger.exception("Failed to store resume: %s", resume_id)


def search_similar_jobs(query: str, top_k: int = 5):
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
    )
    return results