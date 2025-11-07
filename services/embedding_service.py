import os
import numpy as np
from openai import AzureOpenAI

# === Load environment ===
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version="2024-02-15-preview"
)

def get_embedding(text: str):
    """Generate vector embeddings for text using Azure OpenAI."""
    try:
        if not text or not text.strip():
            return None
        response = client.embeddings.create(
            model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            input=text[:8000]  # Azure limits input length
        )
        emb = response.data[0].embedding
        return np.array(emb, dtype=np.float32)
    except Exception as e:
        print(f"⚠️ Embedding generation failed: {e}")
        return None


def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two embeddings."""
    if vec1 is None or vec2 is None:
        return 0.0
    dot = np.dot(vec1, vec2)
    norm = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    if norm == 0:
        return 0.0
    return float(dot / norm)
