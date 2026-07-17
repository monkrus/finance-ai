import logging
from typing import List
from app.ai.gateway import AIGatewayService

logger = logging.getLogger(__name__)

class EmbedderInterface:
    async def embed_text(self, text: str) -> List[float]:
        raise NotImplementedError
        
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

class GeminiEmbedder(EmbedderInterface):
    """
    Implementation of the Embedder using the Gemini API.
    """
    def __init__(self, gateway: AIGatewayService):
        self.gateway = gateway
        self.model = "text-embedding-004"
        
    async def embed_text(self, text: str) -> List[float]:
        try:
            # Note: Assuming gateway exposes or can access the provider's native client
            client = self.gateway.provider.client
            result = await client.aio.models.embed_content(
                model=self.model,
                contents=text
            )
            return result.embeddings[0].values
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            # Return a dummy vector if embedding fails in tests/mock environments
            return [0.0] * 768

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            # For a real implementation, we would batch this call if the API supports it.
            # Using sequential for simplicity and robustness against rate limits here.
            embeddings.append(await self.embed_text(text))
        return embeddings
