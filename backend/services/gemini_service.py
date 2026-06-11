from __future__ import annotations

import json
import logging
from functools import lru_cache
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from adk_agents.exceptions import GeminiServiceError
from config import settings

logger = logging.getLogger("crowdpilot.gemini")

T = TypeVar("T", bound=BaseModel)


class GeminiService:
    """Wrapper around the Gemini API with structured JSON output and logging."""

    def __init__(self) -> None:
        self._client = None

    @property
    def enabled(self) -> bool:
        return bool(settings.gemini_api_key.strip()) and settings.agents_use_gemini

    def _client_instance(self):
        if self._client is not None:
            return self._client

        if not settings.gemini_api_key.strip():
            raise GeminiServiceError("GEMINI_API_KEY is not configured")

        try:
            from google import genai
        except ImportError as exc:
            raise GeminiServiceError(
                "google-genai package is not installed. Run: pip install google-genai"
            ) from exc

        self._client = genai.Client(api_key=settings.gemini_api_key)
        logger.info("Gemini client initialized model=%s", settings.gemini_model)
        return self._client

    def generate_structured(
        self,
        *,
        agent_name: str,
        system_instruction: str,
        user_message: str,
        response_model: type[T],
    ) -> T:
        from google.genai import types

        logger.info(
            "Gemini request start agent=%s model=%s",
            agent_name,
            settings.gemini_model,
        )
        logger.debug("Gemini user payload agent=%s: %s", agent_name, user_message[:2000])

        client = self._client_instance()

        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=settings.gemini_temperature,
                    response_mime_type="application/json",
                    response_schema=response_model,
                ),
            )
        except GeminiServiceError:
            raise
        except Exception as exc:
            logger.exception("Gemini API call failed agent=%s", agent_name)
            raise GeminiServiceError(f"Gemini API call failed for {agent_name}") from exc

        parsed = self._parse_response(response, response_model, agent_name)
        logger.info("Gemini request success agent=%s", agent_name)
        return parsed

    @staticmethod
    def _parse_response(response, response_model: type[T], agent_name: str) -> T:
        if getattr(response, "parsed", None) is not None:
            if isinstance(response.parsed, response_model):
                return response.parsed
            if isinstance(response.parsed, dict):
                return response_model.model_validate(response.parsed)

        text = getattr(response, "text", None)
        if not text:
            logger.error("Gemini returned empty body agent=%s", agent_name)
            raise GeminiServiceError(f"Empty Gemini response for {agent_name}")

        try:
            return response_model.model_validate_json(text)
        except ValidationError:
            pass

        try:
            payload = json.loads(text)
            return response_model.model_validate(payload)
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.error(
                "Gemini JSON validation failed agent=%s snippet=%s",
                agent_name,
                text[:800],
            )
            raise GeminiServiceError(
                f"Gemini returned invalid JSON for {agent_name}"
            ) from exc


@lru_cache
def get_gemini_service() -> GeminiService:
    return GeminiService()
