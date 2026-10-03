import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class GeminiConfigurationError(RuntimeError):
    """Raised when Gemini cannot be configured."""


class GeminiGenerationError(RuntimeError):
    """Raised when Gemini fails to generate a document."""


class GeminiDocumentGenerator:
    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

        if not self.api_key:
            raise GeminiConfigurationError(
                "GEMINI_API_KEY is missing. Add it to your .env file."
            )

        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as exc:
            raise GeminiConfigurationError(
                f"Could not initialize Gemini client: {exc}"
            ) from exc

    @staticmethod
    def _build_prompt(
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        language: str,
    ) -> str:
        return f"""
You are LegalEase's legal-document drafting assistant.

Create a structured DRAFT of the requested legal document using only the facts
provided by the user. Do not invent names, addresses, money amounts, dates,
jurisdictions, statutory citations, registration numbers, or other material facts.

IMPORTANT:
- This is a document draft, not legal advice.
- Do not claim that the document is legally valid in a particular jurisdiction.
- If a jurisdiction-specific issue is required but not supplied, use a neutral
  placeholder such as [JURISDICTION] rather than inventing one.
- Preserve the user's facts accurately.
- Use professional, plain legal language.
- Include sensible headings and numbered clauses.
- Include signature blocks when appropriate.
- Do not wrap the whole response in Markdown code fences.
- Return document text only.

Document type:
{document_type}

Parties:
{parties}

Effective date:
{effective_date}

Terms and conditions:
{terms}

Output language:
{language}
""".strip()

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        language: str = "English",
    ) -> str:
        prompt = self._build_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            effective_date=effective_date,
            language=language,
        )

        try:
            temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.25"))
            max_output_tokens = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "6000"))

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                ),
            )
        except Exception as exc:
            raise GeminiGenerationError(
                f"Gemini request failed: {exc}"
            ) from exc

        text = getattr(response, "text", None)
        if not text or not text.strip():
            raise GeminiGenerationError(
                "Gemini returned an empty response. Check the model name, API key, "
                "quota, and safety response."
            )

        return text.strip()
