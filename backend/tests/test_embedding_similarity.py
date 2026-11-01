from backend.app.services.embedding_service import generate_embedding


def cosine_similarity(vector_a, vector_b):
    """Calculate cosine similarity between two vectors."""

    dot_product = sum(
        a * b for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = sum(a ** 2 for a in vector_a) ** 0.5
    magnitude_b = sum(b ** 2 for b in vector_b) ** 0.5

    return dot_product / (magnitude_a * magnitude_b)


# Three sentences for comparison
sentence_a = "The study investigated malaria prevalence among children."

sentence_b = "The research examined how common malaria is in children."

sentence_c = "The football team won the championship yesterday."


# Generate embeddings
embedding_a = generate_embedding(sentence_a)
embedding_b = generate_embedding(sentence_b)
embedding_c = generate_embedding(sentence_c)


# Calculate similarities
similarity_ab = cosine_similarity(embedding_a, embedding_b)
similarity_ac = cosine_similarity(embedding_a, embedding_c)


print("Similarity between related sentences:", round(similarity_ab, 4))
print("Similarity between unrelated sentences:", round(similarity_ac, 4))