import time
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

    for attempt in range(3):
        try:
            result = gemini_call()
            logger.info("Agent %s completed via Gemini", agent_name)
            return result

        except GeminiServiceError as exc:

            if "503" in str(exc) and attempt < 2:
                logger.warning(
                    "Gemini busy, retrying %s/3...",
                    attempt + 1
                )
                time.sleep(3)
                continue

            logger.warning(
                "Agent %s Gemini failed: %s",
                agent_name,
                exc
            )

            if settings.agent_fallback_to_rules:
                logger.info(
                    "Agent %s falling back to rule-based logic",
                    agent_name
                )
                return rule_call(data)

            raise

    logger.info("Agent %s all Gemini attempts failed, using rule-based logic", agent_name)
    return rule_call(data)