from langchain_core.documents import Document
import logger
from src.config.app_config import app_config
from abc import ABC, abstractmethod
import os
import faiss
from pinecone import ServerlessSpec
from llama_index.vector_stores.faiss import FaissVectorStore
from pinecone import Pinecone as PineconeClient
from llama_index.vector_stores.pinecone import PineconeVectorStore
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from typing import List, Union,Optional
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.schema import Document as LlamaDocument
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
import logging
class VectorStoreStrategy(ABC):
    def __init__(self):
        self.app_config = app_config()

    @abstractmethod
    def store_document(self, document: Union[Document, LlamaDocument, List[Union[Document, LlamaDocument]]], namespace: str):
        pass

    @abstractmethod
    def retrieve_document(self, query: str, namespace: str, filter: dict = None) -> Document:
        pass


class PineCone(VectorStoreStrategy):
    def __init__(self):
        super().__init__()

        # Using getattr in case app_config is a Pydantic model without .get()
        api_key = self.app_config.pinecone_api_key
        index_name = self.app_config.index_name

        self.pc = PineconeClient(api_key=api_key)
        if not self._pc.has_index(index_name):
            logging.info("Index %s not found — creating new Serverless index", index_name)
            
            self.pc.create_index(
                name=index_name,
                dimension=self.retriever_config.embeding_dim,
                metric=self.retriever_config.metric,
                spec=ServerlessSpec(
                    cloud=self.retriever_config.cloud,
                    region=self.retriever_config.region,
                ),
            )
            logger.info("Index %s created successfully", index_name)
        self.pinecone_index = self.pc.Index(index_name)

    def _get_index(self, namespace: str):
        # Pinecone natively supports namespaces.
        # We pass it to the VectorStore and recreate the LlamaIndex wrapper.
        vector_store = PineconeVectorStore(pinecone_index=self.pinecone_index, namespace=namespace)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        return VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

    def store_document(self, document: Union[Document, LlamaDocument, List[Union[Document, LlamaDocument]]], namespace: str):
        index = self._get_index(namespace)

        docs = document if isinstance(document, list) else [document]
        for doc in docs:
            if isinstance(doc, Document):
                llama_doc = LlamaDocument(
                    text=doc.page_content,
                    metadata=doc.metadata or {}
                )
                index.insert(llama_doc)
            else:
                index.insert(doc)

    def retrieve_document(self, query: str, namespace: str, filter: dict = None) -> Document:
        index = self._get_index(namespace)
        filters = None
        if filter:
            filters = MetadataFilters(
                filters=[ExactMatchFilter(key=k, value=v) for k, v in filter.items()]
            )

        retriever = index.as_retriever(similarity_top_k=1, filters=filters)
        nodes = retriever.retrieve(query)
        if not nodes:
            return None

        node = nodes[0]
        return Document(page_content=node.text, metadata=node.metadata)


class Chroma(VectorStoreStrategy):
    def __init__(self):
        super().__init__()

        db_path = getattr(self.app_config, "CHROMA_DB_PATH", os.getenv("CHROMA_DB_PATH", "./chroma_db"))
        self.chroma_client = chromadb.PersistentClient(path=db_path)

    def _get_index(self, namespace: str):
        # Using the namespace as the Chroma collection name for complete separation
        chroma_collection = self.chroma_client.get_or_create_collection(namespace)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        return VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

    def store_document(self, document: Union[Document, LlamaDocument, List[Union[Document, LlamaDocument]]], namespace: str):
        index = self._get_index(namespace)

        docs = document if isinstance(document, list) else [document]
        for doc in docs:
            if isinstance(doc, Document):
                llama_doc = LlamaDocument(
                    text=doc.page_content,
                    metadata=doc.metadata or {}
                )
                index.insert(llama_doc)
            else:
                index.insert(doc)

    def retrieve_document(self, query: str, namespace: str, filter: dict = None) -> Document:
        index = self._get_index(namespace)
        filters = None
        if filter:
            filters = MetadataFilters(
                filters=[ExactMatchFilter(key=k, value=v) for k, v in filter.items()]
            )

        retriever = index.as_retriever(similarity_top_k=1, filters=filters)
        nodes = retriever.retrieve(query)
        if not nodes:
            return None

        node = nodes[0]
        return Document(page_content=node.text, metadata=node.metadata)


class Fiass(VectorStoreStrategy):
    def __init__(self):
        super().__init__()

        self.d = int(getattr(self.app_config, "FAISS_DIMENSIONS", os.getenv("FAISS_DIMENSIONS", "1536")))
        self.namespaces = {}

    def _get_index(self, namespace: str):
        # FAISS is local/in-memory, we can manage separate indexes per namespace in a dict.
        if namespace not in self.namespaces:
            faiss_index = faiss.IndexFlatL2(self.d)
            vector_store = FaissVectorStore(faiss_index=faiss_index)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            self.namespaces[namespace] = VectorStoreIndex.from_vector_store(
                vector_store, storage_context=storage_context
            )
        return self.namespaces[namespace]

    def store_document(self, document: Union[Document, LlamaDocument, List[Union[Document, LlamaDocument]]], namespace: str):
        index = self._get_index(namespace)

        docs = document if isinstance(document, list) else [document]
        for doc in docs:
            if isinstance(doc, Document):
                llama_doc = LlamaDocument(
                    text=doc.page_content,
                    metadata=doc.metadata or {}
                )
                index.insert(llama_doc)
            else:
                index.insert(doc)

    def retrieve_document(self, query: str, namespace: str, filter: dict = None) -> Document:
        index = self._get_index(namespace)
        filters = None
        if filter:
            filters = MetadataFilters(
                filters=[ExactMatchFilter(key=k, value=v) for k, v in filter.items()]
            )

        retriever = index.as_retriever(similarity_top_k=1, filters=filters)
        nodes = retriever.retrieve(query)
        if not nodes:
            return None

        node = nodes[0]
        return Document(page_content=node.text, metadata=node.metadata)


def get_vector_store_strategy(strategy_name: str) -> VectorStoreStrategy:
    strategies = {
        "pinecone": PineCone(),
        "fiass": Fiass(),
        "chroma": Chroma(),
    }

    strategy = strategies.get(strategy_name)
    if not strategy:
        raise ValueError(f"Unknown ingestion strategy: {strategy_name}")

    return strategy
