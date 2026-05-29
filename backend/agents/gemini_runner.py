import logging
from typing import Callable, TypeVar

from agents.exceptions import GeminiServiceError
from config import settings
from services.gemini_service import get_gemini_service

logger = logging.getLogger("crowdpilot.agents")

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


def run_with_gemini_fallback(
    *,
    agent_name: str,
    data: InputT,
    gemini_call: Callable[[], OutputT],
    rule_call: Callable[[InputT], OutputT],
) -> OutputT:
    service = get_gemini_service()

    if not service.enabled:
        logger.info("Agent %s using rule-based logic (Gemini disabled)", agent_name)
        return rule_call(data)

    try:
        result = gemini_call()
        logger.info("Agent %s completed via Gemini", agent_name)
        return result
    except GeminiServiceError as exc:
        logger.warning("Agent %s Gemini failed: %s", agent_name, exc)
        if settings.agent_fallback_to_rules:
            logger.info("Agent %s falling back to rule-based logic", agent_name)
            return rule_call(data)
        raise
