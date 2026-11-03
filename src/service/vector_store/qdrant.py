from functools import lru_cache
from typing import List, Optional, Union, Any
import uuid
import sys

from qdrant_client import AsyncQdrantClient, QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from langchain_core.documents import Document

from src.app_config import get_app_config
from src.core.logger import logger
from src.core.exception import MyException
from src.service.embedding.base import BaseEmbeddingService
from src.service.vector_store.base import BaseVectorStore


class QdrantVectorStore(BaseVectorStore):
    def __init__(
        self,
        collection_name: Optional[str] = None,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        embedding_service: Optional[BaseEmbeddingService] = None,
        **kwargs,
    ):
        super().__init__(embedding_service=embedding_service, **kwargs)
        self.app_config = get_app_config()
        self.collection_name = collection_name or self.app_config.collection_name
        self.url = url or self.app_config.qdrant_cluster_endpoint
        self.api_key = api_key or self.app_config.qdrant_api_key
        self._async_client: Optional[AsyncQdrantClient] = None
        self._sync_client: Optional[QdrantClient] = None

    def get_async_client(self) -> AsyncQdrantClient:
        if self._async_client is None:
            self._async_client = AsyncQdrantClient(
                url=self.url,
                api_key=self.api_key,
                timeout=60
            )
        return self._async_client

    def get_sync_client(self) -> QdrantClient:
        if self._sync_client is None:
            self._sync_client = QdrantClient(
                url=self.url,
                api_key=self.api_key,
            )
        return self._sync_client

    async def ensure_collection(self) -> None:
        with logger.span("qdrant.ensure_collection", collection=self.collection_name):
            try:
                client = self.get_async_client()
                exists = await client.collection_exists(collection_name=self.collection_name)
                if not exists:
                    dim = int(self.app_config.embedding_dim) if self.app_config.embedding_dim else 384
                    await client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
                    )
                    logger.info("qdrant.collection_created", collection=self.collection_name, dim=dim)
                else:
                    logger.debug("qdrant.collection_exists", collection=self.collection_name)
            except Exception:
                logger.exception("qdrant.collection_ensure_failed", collection=self.collection_name)
                raise MyException(sys.exc_info()[1], sys)

    async def upsert(self, documents: Union[Document, List[Document]], **kwargs) -> Any:
        if isinstance(documents, Document):
            documents = [documents]

        if not documents:
            logger.debug("qdrant.empty_upsert", collection=self.collection_name)
            return True

        with logger.span("qdrant.upsert", collection=self.collection_name, count=len(documents)):
            try:
                logger.info("qdrant.upsert_started", collection=self.collection_name, count=len(documents))
                await self.ensure_collection()

                texts = [
                    doc.page_content.decode("utf-8") if isinstance(doc.page_content, bytes) else str(doc.page_content)
                    for doc in documents
                ]
                embeddings = self.embedder.embed_documents(texts)

                points = []
                for doc, emb in zip(documents, embeddings):
                    metadata = doc.metadata.copy() if getattr(doc, "metadata", None) else {}
                    content = (
                        doc.page_content.decode("utf-8")
                        if isinstance(doc.page_content, bytes)
                        else str(doc.page_content)
                    )
                    payload = {
                        "page_content": content,
                        **metadata,
                    }
                    points.append(
                        PointStruct(
                            id=str(uuid.uuid4()),
                            vector=emb,
                            payload=payload,
                        )
                    )

                client = self.get_async_client()
                result = await client.upsert(
                    collection_name=self.collection_name,
                    points=points,
                )
                logger.info("qdrant.upsert_completed", collection=self.collection_name, count=len(points))
                return result or True
            except Exception:
                logger.exception("qdrant.upsert_failed", collection=self.collection_name, count=len(documents))
                raise MyException(sys.exc_info()[1], sys)

    async def similarity_search(self, query: str, k: int = 4, **kwargs) -> List[Document]:
        with logger.span("qdrant.similarity_search", collection=self.collection_name, k=k):
            try:
                logger.info("qdrant.search_started", collection=self.collection_name, query_preview=query[:50], k=k)
                client = self.get_async_client()
                query_vector = self.embedder.embed_query(query)

                search_response = await client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=k,
                    with_payload=True,
                )

                documents = []
                for point in search_response.points:
                    payload = point.payload or {}
                    content = payload.pop("page_content", "")
                    documents.append(Document(page_content=content, metadata=payload))
                logger.info("qdrant.search_completed", collection=self.collection_name, results_count=len(documents))
                return documents
            except Exception:
                logger.exception("qdrant.search_failed", collection=self.collection_name, k=k)
                raise MyException(sys.exc_info()[1], sys)

    def __getattr__(self, name):
        return getattr(self.get_async_client(), name)


@lru_cache
def get_qdrant_service(
    collection_name: Optional[str] = None,
    embedding_service: Optional[BaseEmbeddingService] = None,
) -> QdrantVectorStore:
    return QdrantVectorStore(collection_name=collection_name, embedding_service=embedding_service)
