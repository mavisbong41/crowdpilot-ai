from abc import ABC, abstractmethod
from typing import Generic, TypeVar

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class BaseAgent(ABC, Generic[InputT, OutputT]):
    """Base agent contract. Subclasses implement rule-based or LLM-backed logic."""

    name: str = "base"

    @abstractmethod
    def run(self, data: InputT) -> OutputT:
        """Execute agent logic synchronously."""

    async def arun(self, data: InputT) -> OutputT:
        """Async wrapper for FastAPI route handlers."""
        return self.run(data)
