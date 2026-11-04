from google import genai
from google.genai import types

from backend.app.core.config import settings


def _get_embedding_client():
    if not settings.GOOGLE_GEMINI_TOKEN:
        raise ValueError(
            "Google Gemini API key is not configured."
        )

    return genai.Client(
        api_key=settings.GOOGLE_GEMINI_TOKEN
    )


def generate_embedding(text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("The text cannot be empty.")

    client = _get_embedding_client()

    response = client.models.embed_content(
        model=settings.GEMINI_EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=settings.EMBEDDING_DIMENSION
        )
    )

    return response.embeddings[0].values


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    if any(not text or not text.strip() for text in texts):
        raise ValueError(
            "All texts must contain non-whitespace characters."
        )

    client = _get_embedding_client()

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=768
        )
    )

    return [
        embedding.values
        for embedding in response.embeddings
    ]