from src.nodes.main_nodes import orchastrator_node, retreiver_node, chat_node
from langgraph.graph import StateGraph, START, END
from src.states.Main_State import State
import logging
from src.memory import memory

graph = StateGraph(State)
graph.add_sequence([("orchastrator", orchastrator_node), ("retreiver", retreiver_node), ("chat", chat_node)])
graph.add_edge(START, "orchastrator")
graph.add_edge("chat", END)
graph = graph.compile(checkpointer=memory)





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