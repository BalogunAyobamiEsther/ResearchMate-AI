from sentence_transformers import SentenceTransformer

from backend.app.core.config import settings


# Load the embedding model
embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)


def generate_embedding(text: str) -> list[float]:
    """
    Convert a single text string into a numerical embedding.

    Args:
        text: The input text.

    Returns:
        A list of floating-point numbers representing the text.
    """

    embedding = embedding_model.encode(text)

    return embedding.tolist()


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Convert multiple text strings into numerical embeddings.

    Args:
        texts: A list of text strings.

    Returns:
        A list of embedding vectors, one for each input text.
    """

    # Return an empty list when no texts are provided
    if not texts:
        return []

    # Generate embeddings for all texts in one batch
    embeddings = embedding_model.encode(texts)

    return embeddings.tolist()