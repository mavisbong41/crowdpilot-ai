from fastapi import APIRouter

from config import settings
from services.gemini_service import get_gemini_service

router = APIRouter()


@router.get("/health")
async def health_check():
    gemini_configured = bool(settings.gemini_api_key.strip())
    return {
        "status": "ok",
        "service": "crowdpilot-api",
        "agents": {
            "use_gemini": settings.agents_use_gemini,
            "gemini_configured": gemini_configured,
            "gemini_active": get_gemini_service().enabled,
            "fallback_to_rules": settings.agent_fallback_to_rules,
            "model": settings.gemini_model if gemini_configured else None,
        },
    }
