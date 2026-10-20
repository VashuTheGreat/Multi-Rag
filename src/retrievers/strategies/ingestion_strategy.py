import os
import logging
from abc import ABC, abstractmethod
from typing import List, Any
from langchain_core.documents import Document
from src.entity.config_entity import RetreiverConfig
from llama_parse import LlamaParse
from llama_cloud import LlamaCloud
from llama_index.core import VectorStoreIndex
from langchain_huggingface import HuggingFaceEmbeddings
from src.config.app_config import app_config
from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title
from langchain_community.vectorstores import FAISS
from src.constants import EMBEDDING_MODEL



class CompatibleEmbeddings(HuggingFaceEmbeddings):
    def __call__(self, text: str):
        return self.embed_query(text)




embedding_model = CompatibleEmbeddings(model=EMBEDDING_MODEL)


class IngestionStrategy(ABC):
    @abstractmethod
    async def execute(self, file_path: str, retriever_config: RetreiverConfig) -> str:
        """
        Executes the ingestion strategy on a given file, saves it to the vector store natively,
        and returns the vector store path.
        """
        pass

  

class UnstructuredStrategy(IngestionStrategy):
    async def partition_document(self, file_path: str, retriever_config: RetreiverConfig) -> List[Any]:
        """"""
        logging.info(f"Partitioning document: {file_path}")

        elements = partition_pdf(
            filename=file_path,
            strategy=retriever_config.partition_strategy,
            infer_table_structure=True,
            extract_image_block_types=["Image"],
            extract_image_block_to_payload=True
        )

        logging.info(f"Extracted {len(elements)} elements")
        return elements

    async def create_chunks_by_title(self, elements, retriever_config: RetreiverConfig) -> List[Any]:
        logging.info("Creating smart chunks...")

        chunks = chunk_by_title(
            elements,
            max_characters=retriever_config.max_characters,
            new_after_n_chars=retriever_config.new_after_n_chars,
            combine_text_under_n_chars=retriever_config.combine_text_under_n_chars
        )

        if not chunks and elements:
            logging.warning("chunk_by_title returned 0 chunks, falling back to raw elements.")
            chunks = elements

        logging.info(f"Created {len(chunks)} chunks")
        return chunks

    async def execute(self, file_path: str, retriever_config: RetreiverConfig) -> str:
        logging.info("Executing Unstructured Strategy")
        elements = await self.partition_document(file_path, retriever_config)
        chunks = await self.create_chunks_by_title(elements, retriever_config)

        # Convert unstructured chunks to simple textual Langchain Documents
        documents = []
        for chunk in chunks:
            text = chunk.text if hasattr(chunk, 'text') and chunk.text else str(chunk)
            if text:
                documents.append(Document(page_content=text, metadata={"source": file_path}))

        return documents



class LlamaIndexStrategy(IngestionStrategy):
    async def execute(self, file_path: str,retriever_config: RetreiverConfig) -> str:
        logging.info("Executing LlamaIndex Strategy")

        config = app_config()

        parser = LlamaCloud(
            api_key=config.llama_cloud_api_key or "",
            result_type="markdown",       # preserves tables as markdown
            extract_charts=True,          # extract charts/graphs
            auto_mode=True,
            auto_mode_trigger_on_image_in_page=True,
            auto_mode_trigger_on_table_in_page=True,
        )

        # parser.load_data currently returns LlamaIndex documents
        llama_docs = parser.load_data(file_path)

        

        return llama_docs




def get_ingestion_strategy(strategy_name: str) -> IngestionStrategy:
    strategies = {
        "unstructured": UnstructuredStrategy(),
        "llamaIndex": LlamaIndexStrategy(),
    }

    strategy = strategies.get(strategy_name)
    if not strategy:
        raise ValueError(f"Unknown ingestion strategy: {strategy_name}")

    return strategy


