
import re

from backend.app.services.retrieval_service import retrieve_relevant_chunks
from backend.app.services.prompt_builder import build_rag_prompt
from backend.app.services.llm_service import generate_response


def answer_research_question(
    question: str,
    top_k: int = 5
) -> dict:
    """
    Answer a research question using retrieved evidence
    and validate all generated source citations.
    """

    if not question or not question.strip():
        raise ValueError("The research question cannot be empty.")

    # Step 1: Retrieve relevant passages
    retrieved_chunks = retrieve_relevant_chunks(
        question=question,
        top_k=top_k
    )

    # Step 2: Handle missing evidence
    if not retrieved_chunks:
        return {
            "answer": (
                "I could not find any research evidence "
                "to answer this question."
            ),
            "citations": [],
            "evidence": [],
            "insufficient_evidence": True
        }

    # Step 3: Build the prompt
    rag_data = build_rag_prompt(
        question=question,
        retrieved_chunks=retrieved_chunks
    )

    prompt = rag_data["prompt"]
    sources = rag_data["sources"]

    # Step 4: Generate the response
    generated_response = generate_response(prompt)

    generated_answer = generated_response.answer

    # Step 5: Extract individual IDs from bracketed citations.
    # Supports both [S1] and grouped citations such as [S1, S2].
    citation_groups = re.findall(
        r"\[(S\d+(?:\s*,\s*S\d+)*)\]",
        generated_answer
    )

    referenced_ids = [
        source_id
        for group in citation_groups
        for source_id in re.findall(r"S\d+", group)
    ]

    # Remove duplicate references while preserving their order
    referenced_ids = list(dict.fromkeys(referenced_ids))

    # Step 6: Validate source references
    valid_source_ids = {
        source["source_id"]
        for source in sources
    }

    valid_references = [
        source_id
        for source_id in referenced_ids
        if source_id in valid_source_ids
    ]

    invalid_references = [
        source_id
        for source_id in referenced_ids
        if source_id not in valid_source_ids
    ]

    # Step 7: Build citation metadata
    citations = [
        {
            "source_id": source["source_id"],
            "document_id": source["document_id"],
            "filename": source["filename"],
            "page_number": source["page_number"]
        }
        for source in sources
        if source["source_id"] in valid_references
    ]

    # Step 8: Validate evidence sufficiency
    insufficient_evidence = (
        generated_response.insufficient_evidence
        or len(citations) == 0
        or len(invalid_references) > 0
    )

    return {
        "answer": generated_answer,
        "citations": citations,
        "evidence": sources,
        "insufficient_evidence": insufficient_evidence
    }
