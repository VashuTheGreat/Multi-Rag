from langgraph.graph import StateGraph, START, END

from src.memory import memory
from src.states.Main_State import State

from src.nodes.main_nodes import (
    
    orchastrator_node,
    query_generation_node,
    retreiver_node,
    document_normaliser_node,
    is_retreived_data_enough,
    web_search_node,
    document_refiner,
    get_chat_node_content,
    chat_node
)
from src.nodes.user_nodes import ingestion_node


graph = StateGraph(State)

# ===================== Adding Nodes =====================
graph.add_node(
    "ingestion",
    ingestion_node
)

graph.add_node(
    "orchastrator",
    orchastrator_node
)

graph.add_node(
    "query_generation",
    query_generation_node
)

graph.add_node(
    "retreiver",
    retreiver_node
)

graph.add_node(
    "document_normaliser",
    document_normaliser_node
)

graph.add_node(
    "relevance_checker",
    is_retreived_data_enough
)

graph.add_node(
    "web_search",
    web_search_node
)

graph.add_node(
    "document_refiner",
    document_refiner
)

graph.add_node(
    "context_builder",
    get_chat_node_content
)

graph.add_node(
    "chat",
    chat_node
)

# ===================== Adding Edges =====================
graph.set_conditional_entry_point(
    lambda state: (
        "ingestion"
        if state.get("file_paths")
        else "orchastrator"
    ),
    {
        "ingestion": "ingestion",
        "orchastrator": "orchastrator"
    }
)

graph.add_edge(
    "ingestion",
    END
)


graph.add_conditional_edges(
    "orchastrator",
    lambda state: (
        "query_generation"
        if state.get("require_db_search")
        else "chat"
    ),
    {
        "query_generation": "query_generation",
        "chat": "chat"
    }
)


graph.add_edge(
    "query_generation",
    "retreiver"
)

graph.add_edge(
    "retreiver",
    "document_normaliser"
)

graph.add_edge(
    "document_normaliser",
    "relevance_checker"
)


graph.add_conditional_edges(
    "relevance_checker",
    lambda state: (
        "document_refiner"
        if state["relevance"] == "CORRECT" or state["relevance"] == "AMBIGUOUS"
        else "web_search"
    ),
    {
        "document_refiner": "document_refiner",
        "web_search": "web_search"
    }
)


graph.add_edge(
    "document_refiner",
    "context_builder"
)

graph.add_edge(
    "web_search",
    "context_builder"
)

graph.add_edge(
    "context_builder",
    "chat"
)

graph.add_edge(
    "chat",
    END
)


graph = graph.compile(
    checkpointer=memory
)

try:
    graph.get_graph().draw_mermaid_png(
        output_file_path="graph_visualization.png"
    )
except Exception as e:
    logging.exception(
        f"Failed to generate graph visualization: {e}"
    )



async def deleteThread(thread_id: str):
    try:
        cp = memory
        state = await cp.aget_tuple(config={'configurable': {'thread_id': thread_id}})
        if state is None:
            logging.info(f"Thread {thread_id} not found, nothing to delete.")
            return False
            
        await cp.adelete_thread(thread_id=thread_id)
        logging.info(f"Thread {thread_id} deleted successfully.")
        return True
    except Exception as e:
        logging.error(f"Error deleting thread {thread_id}: {e}")
        return False
    

async def load_conversation(thread_id):
    try:
        state = graph.get_state(config={'configurable': {'thread_id': thread_id}})
        return state.values.get('messages', [])
    except Exception as e:
        logging.error(f"Error loading conversation: {e}")
        return []