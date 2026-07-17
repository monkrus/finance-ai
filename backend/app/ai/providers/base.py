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
