from backend.app.services.llm_service import generate_response


def test_gemini_connection():
    """Test whether ResearchMate AI can communicate with Gemini."""

    prompt = """
    You are an academic research assistant.

    Explain what a descriptive survey research design means
    in three simple sentences.
    """

    response = generate_response(prompt)

    print("\nGemini Response:")
    print(response)

    assert isinstance(response, str)
    assert len(response) > 0


if __name__ == "__main__":
    test_gemini_connection()