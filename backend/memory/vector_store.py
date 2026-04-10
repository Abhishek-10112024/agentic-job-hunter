import chromadb
from chromadb.utils import embedding_functions


# Initialize Chroma client
client = chromadb.Client()

# Use default embedding model
embedding_function = embedding_functions.DefaultEmbeddingFunction()

# Create collection
collection = client.get_or_create_collection(
    name="resume_collection",
    embedding_function=embedding_function
)


def store_resume(resume_id: str, resume_text: str):
    collection.add(
        documents=[resume_text],
        ids=[resume_id]
    )


def search_similar_jobs(query: str, top_k: int = 5):
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    return results