from backend.app.services.llm_service import generate_response


def test_gemini_connection():
    """Test whether ResearchMate AI can communicate with Gemini
    and return a structured response.
    """

    prompt = """
    You are an academic research assistant.

    Explain what a descriptive survey research design means
    in three simple sentences.

    Provide your answer in the required structured response.
    """

    response = generate_response(prompt)

    print("\nGemini Response:")
    print(response.answer)

    print("\nInsufficient Evidence:")
    print(response.insufficient_evidence)

    assert isinstance(response.answer, str)
    assert len(response.answer) > 0
    assert isinstance(response.insufficient_evidence, bool)


if __name__ == "__main__":
    test_gemini_connection()