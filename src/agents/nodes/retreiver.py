from src.app_config import get_app_config
from ..models.state import AgentState
from ...core.exception import MyException
from ...core.logger import logger
from ...service.embedding.sentence_transformer import SentenceTransformerEmbedding, get_embedding_service
from ...service.vector_store.qdrant import QdrantVectorStore, get_qdrant_service
from langsmith import traceable
import sys

observe = traceable

app_config = get_app_config()
embedding_service: SentenceTransformerEmbedding = get_embedding_service()
vector_store_service: QdrantVectorStore = get_qdrant_service(collection_name=app_config.collection_name, embedding_service=embedding_service)


@observe(name="retriever_node", run_type="retriever")
async def retreived_node(state: AgentState):
    """Fetching relevant similar dcuments according to query"""
    queries = state.get("queries")
    with logger.span("Retriever node execution", queries=queries):
        try:
            logger.info("Querying vector store for documents", queries=queries)
            documents = await vector_store_service.similarity_search(query=queries)
            doc_count = len(documents) if documents else 0
            logger.info("Documents retrieved successfully", count=doc_count)
            return {"retreived_content": documents}
        except Exception as e:
            logger.error("Document retrieval failed", error=str(e))
            raise MyException(e, sys)