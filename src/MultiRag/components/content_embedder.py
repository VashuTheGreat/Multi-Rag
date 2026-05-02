
from utils.asyncHandler import asyncHandler
from src.MultiRag.entity.config_entity import ContentEmbedderConfig
from src.MultiRag.utils.ingestion_utils import create_vector_store,create_retreiver
from src.MultiRag.constants import RETREIVER_DEFAULT_K
from src.MultiRag.entity.artifact_entity import RetrievalArtifact
from abc import ABC, abstractmethod
import logging


class Retreiver(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def retreive(self, query: str):
        pass

class ContentRetreiver(Retreiver):
    def __init__(self, retriever):
        self.retriever = retriever

    async def retreive(self, query: str):
        return await self.retriever.ainvoke(query)
class ContentEmbedder:
    def __init__(self, content_embedder_config: ContentEmbedderConfig):
        self.content_embedder_config = content_embedder_config


    @asyncHandler
    async def embed_PDF(self):
        vector_store = await create_vector_store(path=self.content_embedder_config.vector_store_path, docs=self.content_embedder_config.file_path)
        return vector_store

    @asyncHandler
    async def create_retriever(self,vector_store, k:int = RETREIVER_DEFAULT_K)->RetrievalArtifact:
        retriever = await create_retreiver(vectorstore=vector_store, k=k)
        return retriever
    



    @asyncHandler
    async def embed_content(self)->RetrievalArtifact:
        logging.info("Starting content embedding process...")

        vector_store = await self.embed_PDF()
        if vector_store is None:
            logging.warning("No vector store created. Returning empty artifact.")
            return RetrievalArtifact(retreivar=None)

        logging.info("PDF embedding completed. Creating retriever...")
        retriever = await self.create_retriever(vector_store=vector_store)

        content_retriever = ContentRetreiver(retriever=retriever)
        logging.info("Retriever created successfully.")
        return RetrievalArtifact(retreivar=content_retriever)
        