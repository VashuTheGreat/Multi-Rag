from functools import lru_cache
from typing import List, Optional
import sys

from src.app_config import get_app_config
from src.core.logger import logger
from src.core.exception import MyException
from src.service.embedding.base import BaseEmbeddingService


class SentenceTransformerEmbedding(BaseEmbeddingService):
    def __init__(self, model_name: Optional[str] = None):
        self.app_config = get_app_config()
        self.model_name = model_name or self.app_config.embedding_model or "all-MiniLM-L6-v2"
        self._model = None

    def _get_model(self):
        if self._model is None:
            with logger.span("🧠 Initializing SentenceTransformer model: {model}", model=self.model_name):
                try:
                    from sentence_transformers import SentenceTransformer
                    logger.info("🧠 Loading SentenceTransformer model weights", model=self.model_name)
                    self._model = SentenceTransformer(self.model_name)
                    logger.info("✅ SentenceTransformer model ready", model=self.model_name)
                except Exception as e:
                    logger.error("❌ Failed to load SentenceTransformer model", model=self.model_name, error=str(e))
                    raise MyException(e, sys)
        return self._model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            logger.debug("⚠️ Empty text list provided for embedding")
            return []
        with logger.span("🔢 Embedding {count} documents", count=len(texts)):
            try:
                logger.info("🧠 Generating embeddings for document batch", count=len(texts))
                model = self._get_model()
                embeddings = model.encode(texts)
                logger.info("✅ Document embeddings generated successfully", count=len(texts))
                return [emb.tolist() for emb in embeddings]
            except Exception as e:
                logger.error("❌ Failed to embed document batch", error=str(e))
                raise MyException(e, sys)

    def embed_query(self, text: str) -> List[float]:
        with logger.span("🔍 Embedding query"):
            try:
                logger.info("🧠 Generating query embedding", query_len=len(text))
                model = self._get_model()
                embedding = model.encode(text)
                logger.info("✅ Query embedding generated successfully")
                return embedding.tolist()
            except Exception as e:
                logger.error("❌ Failed to embed query", error=str(e))
                raise MyException(e, sys)


@lru_cache
def get_embedding_service(model_name: Optional[str] = None) -> BaseEmbeddingService:
    return SentenceTransformerEmbedding(model_name=model_name)
