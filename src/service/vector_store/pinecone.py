from functools import lru_cache
from typing import List, Optional, Union, Any
import uuid
import sys
import os

from langchain_core.documents import Document

from src.app_config import get_app_config
from src.core.logger import logger
from src.core.exception import MyException
from src.service.embedding.base import BaseEmbeddingService
from src.service.vector_store.base import BaseVectorStore


class PineconeVectorStore(BaseVectorStore):
    def __init__(
        self,
        index_name: Optional[str] = None,
        api_key: Optional[str] = None,
        embedding_service: Optional[BaseEmbeddingService] = None,
        **kwargs,
    ):
        super().__init__(embedding_service=embedding_service, **kwargs)
        self.app_config = get_app_config()
        self.index_name = index_name or getattr(self.app_config, "collection_name", None) or "default-index"
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self._pc = None
        self._index = None

    def _get_client(self):
        if self._pc is None:
            try:
                from pinecone import Pinecone
                if not self.api_key:
                    raise ValueError("PINECONE_API_KEY is not set or provided.")
                logger.info("pinecone.client_initializing")
                self._pc = Pinecone(api_key=self.api_key)
                logger.info("pinecone.client_initialized", index=self.index_name)
            except ImportError:
                raise ImportError("Pinecone client is not installed. Install with `pip install pinecone`.")
            except Exception:
                logger.exception("pinecone.client_init_failed")
                raise MyException(sys.exc_info()[1], sys)
        return self._pc

    def _get_index(self):
        if self._index is None:
            pc = self._get_client()
            self._index = pc.Index(self.index_name)
        return self._index

    async def ensure_collection(self) -> None:
        with logger.span("pinecone.ensure_collection", index=self.index_name):
            try:
                pc = self._get_client()
                existing_indexes = [idx.name for idx in pc.list_indexes()]
                if self.index_name not in existing_indexes:
                    dim = int(self.app_config.embedding_dim) if self.app_config.embedding_dim else 384
                    from pinecone import ServerlessSpec
                    pc.create_index(
                        name=self.index_name,
                        dimension=dim,
                        metric="cosine",
                        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                    )
                    logger.info("pinecone.index_created", index=self.index_name, dim=dim)
                else:
                    logger.debug("pinecone.index_exists", index=self.index_name)
            except Exception:
                logger.exception("pinecone.collection_ensure_failed", index=self.index_name)
                raise MyException(sys.exc_info()[1], sys)

    async def upsert(self, documents: Union[Document, List[Document]], **kwargs) -> Any:
        if isinstance(documents, Document):
            documents = [documents]

        if not documents:
            logger.debug("pinecone.empty_upsert", index=self.index_name)
            return True

        with logger.span("pinecone.upsert", index=self.index_name, count=len(documents)):
            try:
                logger.info("pinecone.upsert_started", index=self.index_name, count=len(documents))
                await self.ensure_collection()

                texts = [
                    doc.page_content.decode("utf-8") if isinstance(doc.page_content, bytes) else str(doc.page_content)
                    for doc in documents
                ]
                embeddings = self.embedder.embed_documents(texts)

                vectors = []
                for doc, emb in zip(documents, embeddings):
                    metadata = doc.metadata.copy() if getattr(doc, "metadata", None) else {}
                    content = (
                        doc.page_content.decode("utf-8")
                        if isinstance(doc.page_content, bytes)
                        else str(doc.page_content)
                    )
                    metadata["page_content"] = content

                    vectors.append({
                        "id": str(uuid.uuid4()),
                        "values": emb,
                        "metadata": metadata,
                    })

                index = self._get_index()
                result = index.upsert(vectors=vectors)
                logger.info("pinecone.upsert_completed", index=self.index_name, count=len(vectors))
                return result or True
            except Exception:
                logger.exception("pinecone.upsert_failed", index=self.index_name, count=len(documents))
                raise MyException(sys.exc_info()[1], sys)

    async def similarity_search(self, query: str, k: int = 4, **kwargs) -> List[Document]:
        with logger.span("pinecone.similarity_search", index=self.index_name, k=k):
            try:
                logger.info("pinecone.search_started", index=self.index_name, query_preview=query[:50], k=k)
                query_vector = self.embedder.embed_query(query)
                index = self._get_index()
                response = index.query(vector=query_vector, top_k=k, include_metadata=True)

                documents = []
                for match in response.get("matches", []):
                    meta = match.get("metadata", {})
                    content = meta.pop("page_content", "")
                    documents.append(Document(page_content=content, metadata=meta))
                logger.info("pinecone.search_completed", index=self.index_name, results_count=len(documents))
                return documents
            except Exception:
                logger.exception("pinecone.search_failed", index=self.index_name, k=k)
                raise MyException(sys.exc_info()[1], sys)


@lru_cache
def get_pinecone_service(
    index_name: Optional[str] = None,
    embedding_service: Optional[BaseEmbeddingService] = None,
) -> PineconeVectorStore:
    return PineconeVectorStore(index_name=index_name, embedding_service=embedding_service)
