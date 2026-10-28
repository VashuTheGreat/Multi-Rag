from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from src.agents.models.state import AgentState
from src.agents.nodes.planner import planner_node
from src.agents.nodes.responder import responder_node
from src.agents.nodes.retreiver import retreived_node
from src.core.logger import logger
from functools import lru_cache
from src.service.memory.inmemory import get_memory



memory  = get_memory()



def route_decision(state: AgentState) -> str:
    route = state.get("route_to", "responder")
    if route == "retriever":
        logger.info("🔀 Routing to retriever node", route=route)
        return "retriever"
    logger.info("🔀 Routing directly to responder node", route=route)
    return "responder"



def create_agent_graph(checkpointer=None) -> CompiledStateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("planner", planner_node)
    builder.add_node("retriever", retreived_node)
    builder.add_node("responder", responder_node)

    builder.add_edge(START, "planner")
    builder.add_conditional_edges(
        "planner",
        route_decision,
        {
            "retriever": "retriever",
            "responder": "responder",
        },
    )
    builder.add_edge("retriever", "responder")
    builder.add_edge("responder", END)

    return builder.compile(checkpointer=checkpointer)



@lru_cache
def get_graph() -> CompiledStateGraph:
    with logger.span("🕸️ Compiling multi-agent RAG graph"):
        logger.info("🕸️ Initializing agent StateGraph builder")
        compiled = create_agent_graph(checkpointer=memory)
        logger.info("✅ Multi-agent RAG graph compiled successfully")
        return compiled


graph = get_graph()
