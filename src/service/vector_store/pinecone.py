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
                logger.info("🌲 Initializing Pinecone client")
                self._pc = Pinecone(api_key=self.api_key)
                logger.info("✅ Pinecone client initialized successfully")
            except ImportError:
                raise ImportError("Pinecone client is not installed. Install with `pip install pinecone`.")
            except Exception as e:
                logger.error("❌ Failed to initialize Pinecone client", error=str(e))
                raise MyException(e, sys)
        return self._pc

    def _get_index(self):
        if self._index is None:
            pc = self._get_client()
            self._index = pc.Index(self.index_name)
        return self._index

    async def ensure_collection(self) -> None:
        with logger.span("📦 Ensuring Pinecone index: {index}", index=self.index_name):
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
                    logger.info("📦 Created Pinecone index", index=self.index_name, dim=dim)
                else:
                    logger.debug("📦 Pinecone index already exists", index=self.index_name)
            except Exception as e:
                logger.error("❌ Failed to ensure Pinecone index", index=self.index_name, error=str(e))
                raise MyException(e, sys)

    async def upsert(self, documents: Union[Document, List[Document]], **kwargs) -> Any:
        if isinstance(documents, Document):
            documents = [documents]

        if not documents:
            logger.debug("⚠️ No documents to upsert to Pinecone")
            return True

        with logger.span("📤 Upserting documents to Pinecone: {index}", index=self.index_name, count=len(documents)):
            try:
                logger.info("📤 Preparing documents for Pinecone upsert", index=self.index_name, count=len(documents))
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
                logger.info("✅ Documents upserted to Pinecone successfully", index=self.index_name, count=len(vectors))
                return result or True
            except Exception as e:
                logger.error("❌ Failed to upsert to Pinecone", index=self.index_name, error=str(e))
                raise MyException(e, sys)

    async def similarity_search(self, query: str, k: int = 4, **kwargs) -> List[Document]:
        with logger.span("🔎 Pinecone similarity search: {index}", index=self.index_name, k=k):
            try:
                logger.info("🔎 Searching in Pinecone", index=self.index_name, query_preview=query[:50], k=k)
                query_vector = self.embedder.embed_query(query)
                index = self._get_index()
                response = index.query(vector=query_vector, top_k=k, include_metadata=True)

                documents = []
                for match in response.get("matches", []):
                    meta = match.get("metadata", {})
                    content = meta.pop("page_content", "")
                    documents.append(Document(page_content=content, metadata=meta))
                logger.info("✅ Pinecone search returned matches", index=self.index_name, results_count=len(documents))
                return documents
            except Exception as e:
                logger.error("❌ Similarity search failed in Pinecone", index=self.index_name, error=str(e))
                raise MyException(e, sys)


@lru_cache
def get_pinecone_service(
    index_name: Optional[str] = None,
    embedding_service: Optional[BaseEmbeddingService] = None,
) -> PineconeVectorStore:
    return PineconeVectorStore(index_name=index_name, embedding_service=embedding_service)
