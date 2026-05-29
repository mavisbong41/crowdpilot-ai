class AgentError(Exception):
    """Base error for agent execution."""


class GeminiServiceError(AgentError):
    """Raised when the Gemini API call or response parsing fails."""
