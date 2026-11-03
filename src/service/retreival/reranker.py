from langchain_core.documents import Document
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank
import asyncio
from src.core.logger import logger
from src.core.exception import MyException
import sys


reranker_compressor = FlashrankRerank()

async def flaskreranker(query:str,documents:list[Document]):
    """Rerank the retrieved documents based on relevance to the query"""
    try:
        logger.info("Reranking documents for query", query=query)
        reranked_documents = await asyncio.to_thread(reranker_compressor.compress_documents, query=query, documents=documents)

        logger.info("Documents reranked successfully", count=len(reranked_documents))
        return {"reranked_content": reranked_documents}
    except Exception as e:
        logger.error("Document reranking failed", error=str(e))
        raise MyException(e, sys)