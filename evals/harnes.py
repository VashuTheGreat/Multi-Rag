import os
import sys
import json
from typing import Any
from dotenv import load_dotenv

load_dotenv()
# Prevent LangSmith agent addressing conflict with evaluation sessions
os.environ.pop("LANGSMITH_AGENT_ID", None)
os.environ.pop("LANGSMITH_AGENT_ENVIRONMENT", None)

from langchain_nvidia_ai_endpoints import ChatNVIDIA
from src.agents.graph import create_agent_graph
from src.service.vector_store.qdrant import get_qdrant_service
from src.service.embedding.sentence_transformer import get_embedding_service
from src.app_config import get_app_config
from src.core.exception import MyException

# Judge model for evaluation
judge = ChatNVIDIA(model="nvidia/nemotron-3-ultra-550b-a55b")

# Multi-RAG agent pipeline graph
_graph = create_agent_graph()

# Vector store retriever service
_app_config = get_app_config()
_embedding_service = get_embedding_service()
_vector_store = get_qdrant_service(
    collection_name=_app_config.collection_name,
    embedding_service=_embedding_service,
)


def load_data(file_path: str) -> list[dict[str, Any]]:
    """Loads golden dataset from json file."""
    try:
        with open(file=file_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise MyException(e, sys)


async def run_retriever_node(query: str) -> dict:
    """Sirf retriever node tak ka state run karne ke liye _graph ka use."""
    initial_state = {
        "user_message": query,
        "messages": [],
        "retreived_content": None,
        "queries": None,
    }
    
    # Agar aapko graph ko beech me (retriever ke baad) rokna hai ya sirf wahan tak chalana hai
    async for event in _graph.astream(initial_state, stream_mode="updates"):
        if "retriever" in event:  // yahan apne retriever node ka naam dein
            return event["retriever"]
            
    return {}

async def run_agent(query: str) -> dict:
    """Executes the full Multi-RAG agent pipeline (planner, retriever, responder)."""
    state = await _graph.ainvoke({
        "user_message": query,
        "messages": [],
        "retreived_content": None,
        "queries": None,
    })
    messages = state.get("messages") or []
    answer = messages[-1].content if messages else ""
    return {
        "response": answer,
        "retrieved_content": state.get("retreived_content") or [],
        "route_to": state.get("route_to", "responder"),
    }

async def run_generator_node(state: dict) -> dict:
    """Generator/Responder node ko run karne ke liye _graph ka use."""
    # Agar state me already retrieved content hai, toh seedha generator node chalega
    async for event in _graph.astream(state, stream_mode="updates"):
        if "responder" in event:  // ya generator/responder node ka naam
            return event["responder"]
            
    return {}
