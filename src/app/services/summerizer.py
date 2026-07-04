from src.app.core.config import get_settings

from google import genai

settings = get_settings()


class Summarizer:

    _client: genai.Client | None = None

    @classmethod
    def _get_client(cls) -> genai.Client:
        if cls._client is None:
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                raise RuntimeError("GEMINI_API_KEY is not set in the environment.")
            cls._client = genai.Client(api_key=api_key)
        return cls._client

    @classmethod
    def gemini(cls, prompt: str) -> str:
        client = cls._get_client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text