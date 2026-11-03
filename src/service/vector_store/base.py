from abc import ABC, abstractmethod
from typing import List, Optional, Union, Any, Dict
from langchain_core.documents import Document

from src.service.embedding.base import BaseEmbeddingService
from src.service.embedding.sentence_transformer import get_embedding_service


class BaseVectorStore(ABC):
    """Abstract base class for vector store services."""

    def __init__(self, embedding_service: Optional[BaseEmbeddingService] = None, **kwargs):
        self._embedding_service = embedding_service

    @property
    def embedder(self) -> BaseEmbeddingService:
        """Lazily initialize or return the provided embedding service."""
        if self._embedding_service is None:
            self._embedding_service = get_embedding_service()
        return self._embedding_service

    @abstractmethod
    async def ensure_collection(self) -> None:
        """Ensure that the vector collection/index exists."""
        pass

    @abstractmethod
    async def upsert(self, documents: Union[Document, List[Document]], **kwargs) -> Any:
        """Upsert documents into the vector store."""
        pass

    @abstractmethod
    async def similarity_search(self, query: str, k: int = 4, **kwargs) -> List[Document]:
        """Search for documents similar to query."""
        pass
