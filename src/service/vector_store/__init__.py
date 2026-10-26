from typing import Optional
from src.service.embedding.base import BaseEmbeddingService
from src.service.vector_store.base import BaseVectorStore
from src.service.vector_store.qdrant import QdrantVectorStore, get_qdrant_service
from src.service.vector_store.pinecone import PineconeVectorStore, get_pinecone_service

# Aliases
VectorStoreClient = QdrantVectorStore
get_client = get_qdrant_service


def get_vector_store(
    provider: str = "qdrant",
    collection_name: Optional[str] = None,
    embedding_service: Optional[BaseEmbeddingService] = None,
    **kwargs,
) -> BaseVectorStore:
    """Factory function to get vector store by provider name."""
    provider_lower = provider.lower()
    if provider_lower == "qdrant":
        return get_qdrant_service(collection_name=collection_name, embedding_service=embedding_service)
    elif provider_lower == "pinecone":
        return get_pinecone_service(index_name=collection_name, embedding_service=embedding_service)
    else:
        raise ValueError(f"Unsupported vector store provider: '{provider}'. Supported providers: 'qdrant', 'pinecone'")


__all__ = [
    "BaseVectorStore",
    "QdrantVectorStore",
    "PineconeVectorStore",
    "VectorStoreClient",
    "get_client",
    "get_qdrant_service",
    "get_pinecone_service",
    "get_vector_store",
]
