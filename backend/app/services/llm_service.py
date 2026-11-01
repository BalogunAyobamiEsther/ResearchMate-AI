from google import genai

from backend.app.core.config import settings


def generate_response(prompt: str) -> str:
    """
    Send a prompt to Google Gemini and return its response.

    Args:
        prompt: The text prompt sent to the LLM.

    Returns:
        The generated text response.
    """

    # Validate the prompt
    if not prompt.strip():
        raise ValueError("The prompt cannot be empty.")

    # Check whether the API key is configured
    if not settings.GOOGLE_GEMINI_TOKEN:
        raise ValueError("Google Gemini API key is not configured.")

    # Create a Gemini API client
    client = genai.Client(
        api_key=settings.GOOGLE_GEMINI_TOKEN
    )

    # Send the prompt to Gemini
    response = client.models.generate_content(
        model=settings.LLM_MODEL,
        contents=prompt
    )

    # Check whether Gemini returned a response
    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text.strip()