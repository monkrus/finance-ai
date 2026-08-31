from abc import ABC, abstractmethod
from typing import List, AsyncGenerator
from app.ai.models import AIMessage, AIResponse, AITool

class AIProviderInterface(ABC):
    """
    Abstract interface for all LLM providers (Gemini, Claude, OpenAI).
    """

    @abstractmethod
    async def generate_content(
        self,
        messages: List[AIMessage],
        tools: List[AITool] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AIResponse:
        """
        Generate a complete response from the AI model.
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[AIMessage],
        tools: List[AITool] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from the AI model.
        """
        pass

    async def generate_structured(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AIResponse:
        """
        Generate a single-turn response constrained to JSON.

        Not abstract: providers without native structured-output support can
        inherit this and fail loudly rather than silently returning prose that
        downstream JSON parsing would choke on.
        """
        raise NotImplementedError(
            f"{type(self).__name__} does not implement structured generation."
        )
