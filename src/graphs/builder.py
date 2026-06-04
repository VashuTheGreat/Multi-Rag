from src.nodes.main_nodes import orchastrator_node, retreiver_node, chat_node
from langgraph.graph import StateGraph, START, END
from src.states.Main_State import State

from src.memory import memory

graph = StateGraph(State)
graph.add_sequence([("orchastrator", orchastrator_node), ("retreiver", retreiver_node), ("chat", chat_node)])
graph.add_edge(START, "orchastrator")
graph.add_edge("chat", END)
graph = graph.compile(checkpointer=memory)
