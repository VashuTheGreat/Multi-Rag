import os
import logging
from typing import List
from src.utils.asyncHandler import asyncHandler


from langchain_core.documents import Document
from src.entity.config_entity import RetreiverConfig
from src.constants import INGESTION_STRATEGY_NAME, VECTOR_STORE_STRATEGY_NAME
from src.retrievers.strategies.ingestion_strategy import get_ingestion_strategy
from src.retrievers.strategies.vector_store_strategy import get_vector_store_strategy


class Retreiver:
    def __init__(self, retreiver_config: RetreiverConfig):
        self.retreiver_config = retreiver_config

   
  

    # @asyncHandler
    # async def create_retreiver(self, vectorstore):
    #     logging.info("Extracting documents from vectorstore for BM25...")
    #     documents = list(vectorstore.docstore._dict.values())
    #     base_k = max(self.retreiver_config.k * 2, 20)
    #     vector_retriever = vectorstore.as_retriever(search_kwargs={"k": base_k})
    #     valid_documents = [doc for doc in documents if doc.page_content and doc.page_content.strip()]
    #     if not valid_documents:
    #         logging.info("No documents with text content found in vectorstore docstore. Returning vector retriever.")
    #         return vector_retriever
    #     bm25_retriever = BM25Retriever.from_documents(valid_documents)
    #     bm25_retriever.k = base_k
    #     hybrid_retriever = EnsembleRetriever(
    #         retrievers=[vector_retriever, bm25_retriever],
    #         weights=self.retreiver_config.ensemble_weights
    #     )
    #     return hybrid_retriever

    @asyncHandler
    async def ingest(self, file_path: str, namespace: str):
        logging.info(f"loading vectorstore acc to strategy {INGESTION_STRATEGY_NAME}")

        ingestion_strategy=get_ingestion_strategy(INGESTION_STRATEGY_NAME)



        documents = await ingestion_strategy.execute(file_path=file_path, retriever_config=self.retreiver_config)

        vectorstore_strategy = get_vector_store_strategy(VECTOR_STORE_STRATEGY_NAME)


        vectorstore = vectorstore_strategy.store_document(documents, namespace=namespace)

        return vectorstore



    @asyncHandler
    async def query_retreiver(self, query:str,namespace:str, filter:dict=None):
        logging.info(f"loading vectorstore acc to strategy {VECTOR_STORE_STRATEGY_NAME}")

        vectorstore_strategy = get_vector_store_strategy(VECTOR_STORE_STRATEGY_NAME)

        documents = vectorstore_strategy.retrieve_document(query=query, namespace=namespace, filter=filter)

        return documents
            

    
    

    # @asyncHandler
    # async def merge_vector_stores(self, vector_store_paths: List[str]):
    #     logging.info(f"Merging {len(vector_store_paths)} vector stores")
        
    #     individual_retrievers = []
    #     for path in vector_store_paths:
    #         if os.path.exists(path):
    #             vectorstore = FAISS.load_local(
    #                 path, 
    #                 embedding_model, 
    #                 allow_dangerous_deserialization=True
    #             )
    #             retriever = await self.create_retreiver(vectorstore)
    #             individual_retrievers.append(retriever)
        
    #     if not individual_retrievers:
    #         logging.warning("No valid vector stores found to merge")
    #         return None
            
    #     weights = [1.0 / len(individual_retrievers)] * len(individual_retrievers)
        
    #     hybrid_retriever = EnsembleRetriever(
    #         retrievers=individual_retrievers,
    #         weights=weights
    #     )


    #     compressor = FlashrankRerank(top_n=self.retreiver_config.k)

    #     compression_retriever = ContextualCompressionRetriever(
    #         base_compressor=compressor,
    #         base_retriever=hybrid_retriever
    #     )

    #     return compression_retriever
        
