from abc import ABC, abstractmethod
from typing import List


class BaseEmbeddingService(ABC):
    """Abstract base class for all embedding service providers."""

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of text documents into vector representations."""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text into a vector representation."""
        pass
