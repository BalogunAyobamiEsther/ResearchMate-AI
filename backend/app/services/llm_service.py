
from google import genai
from google.genai import types
from google.genai.errors import ServerError

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from backend.app.core.config import settings
from backend.app.schemas.chat import LLMResponse


def generate_response(prompt: str) -> LLMResponse:
    """
    Send a prompt to Google Gemini and return a structured response.

    Temporary Gemini server errors are retried automatically.
    """

    if not prompt or not prompt.strip():
        raise ValueError("The prompt cannot be empty.")

    if not settings.GOOGLE_GEMINI_TOKEN:
        raise ValueError("Google Gemini API key is not configured.")

    client = genai.Client(
        api_key=settings.GOOGLE_GEMINI_TOKEN
    )

    @retry(
        retry=retry_if_exception_type(ServerError),
        wait=wait_exponential(
            multiplier=2,
            min=2,
            max=10
        ),
        stop=stop_after_attempt(3),
        reraise=True
    )
    def call_gemini():
        return client.models.generate_content(
            model=settings.LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=LLMResponse.model_json_schema()
            )
        )

    response = call_gemini()

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return LLMResponse.model_validate_json(response.text)
