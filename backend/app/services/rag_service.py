import re

from backend.app.services.retrieval_service import retrieve_relevant_chunks
from backend.app.services.prompt_builder import build_rag_prompt
from backend.app.services.llm_service import generate_response


def answer_research_question(
    question: str,
    top_k: int = 5
) -> dict:
    """
    Answer a research question using Retrieval-Augmented Generation.

    Args:
        question: The user's research question.
        top_k: Number of relevant passages to retrieve.

    Returns:
        A dictionary containing the answer, citations,
        supporting evidence and evidence status.
    """

    # Validate the research question
    if not question.strip():
        raise ValueError("The research question cannot be empty.")

    # Step 1: Retrieve relevant research passages
    retrieved_chunks = retrieve_relevant_chunks(
        question=question,
        top_k=top_k
    )

    # Step 2: Handle cases where no passages are retrieved
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

    # Step 3: Construct the RAG prompt
    rag_data = build_rag_prompt(
        question=question,
        retrieved_chunks=retrieved_chunks
    )

    prompt = rag_data["prompt"]
    sources = rag_data["sources"]

    # Step 4: Generate an answer using Gemini
    generated_answer = generate_response(prompt)

    # Step 5: Extract source references from the answer
    referenced_ids = re.findall(
        r"\[(S\d+)\]",
        generated_answer
    )

    # Step 6: Validate references against retrieved sources
    valid_source_ids = {
        source["source_id"]
        for source in sources
    }

    valid_references = list(dict.fromkeys(
        source_id
        for source_id in referenced_ids
        if source_id in valid_source_ids
    ))

    # Step 7: Map valid references to actual document metadata
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

    # Step 8: Identify whether the answer has valid citations
    insufficient_evidence = len(citations) == 0

    return {
        "answer": generated_answer,
        "citations": citations,
        "evidence": sources,
        "insufficient_evidence": insufficient_evidence
    }