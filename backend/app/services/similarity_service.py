import httpx
from app.core.config import settings
import math

class SimilarityService:
    def __init__(self):
        self.base_url = settings.API_BASE or settings.OPENAI_BASE_URL
        self.api_key = settings.EMBEDDING_API_KEY or settings.OPENAI_API_KEY
        self.embedding_model = settings.EMBEDDING_MODEL_NAME
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )

    async def get_embedding(self, text: str) -> list[float]:
        """
        Gets a text embedding from the API.
        """
        if not text:
            return []

        try:
            response = await self.client.post(
                "/embeddings",
                json={"input": text, "model": self.embedding_model}
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
        except Exception as e:
            print(f"Error getting embedding for '{text}': {e}")
            return []

    def cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """
        Calculates the cosine similarity between two vectors.
        Pure Python implementation.
        """
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(v1**2 for v1 in vec1))
        magnitude2 = math.sqrt(sum(v2**2 for v2 in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

similarity_service = SimilarityService()
