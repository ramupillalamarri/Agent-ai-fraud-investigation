from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class LLMProvider(ABC):
    """Abstract interface representing a Large Language Model generation service (e.g. Gemini, OpenAI)."""

    @abstractmethod
    def generate(self, prompt: str, system_instruction: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> str:
        """Sends a query prompt to the LLM and returns the text response."""
        pass
