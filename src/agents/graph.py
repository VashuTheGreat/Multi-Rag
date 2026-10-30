from functools import lru_cache

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from src.agents.models.state import AgentState
from src.agents.nodes.guardrail import guardrail_node, blocked_responder_node
from src.agents.nodes.planner import planner_node
from src.agents.nodes.responder import responder_node
from src.agents.nodes.retreiver import retreived_node
from src.core.logger import logger


def guardrail_decision(state: AgentState) -> str:
    if state.get("is_blocked"):
        logger.warning("Guardrail blocked execution, routing to blocked_responder")
        return "blocked_responder"
    logger.info("Guardrail passed, routing to planner")
    return "planner"


def route_decision(state: AgentState) -> str:
    route = state.get("route_to", "responder")
    if route == "retriever":
        logger.info("Routing to retriever node", route=route)
        return "retriever"
    logger.info("Routing directly to responder node", route=route)
    return "responder"


def create_agent_graph(checkpointer=None) -> CompiledStateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("guardrail", guardrail_node)
    builder.add_node("blocked_responder", blocked_responder_node)
    builder.add_node("planner", planner_node)
    builder.add_node("retriever", retreived_node)
    builder.add_node("responder", responder_node)

    builder.add_edge(START, "guardrail")
    builder.add_conditional_edges(
        "guardrail",
        guardrail_decision,
        {
            "blocked_responder": "blocked_responder",
            "planner": "planner",
        },
    )
    builder.add_edge("blocked_responder", END)
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



@lru_cache(maxsize=2)
def get_graph(checkpointer: AsyncSqliteSaver | None) -> CompiledStateGraph:
    cp = checkpointer
    if cp is None:
        raise RuntimeError("The checkpointer must be initialized before creating the agent graph.")

    with logger.span("Compiling multi-agent RAG graph", has_checkpointer=cp is not None):
        logger.info("Initializing agent StateGraph builder", checkpointer=type(cp).__name__)
        graph = create_agent_graph(checkpointer=cp)
        logger.info("Multi-agent RAG graph compiled successfully")
        return graph

