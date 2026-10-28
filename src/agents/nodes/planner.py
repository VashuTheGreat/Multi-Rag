from src.service.llm_provider.groq import get_llm
from ..models.state import AgentState
from ..models.structure import PlannerStructure
from ..prompts import PLANNER_PROMPT
from ...core.exception import MyException
from ...core.logger import logger
from langsmith import traceable
import sys

observe = traceable

llm = get_llm()


@observe(name="planner_node", run_type="chain")
async def planner_node(state: AgentState):
    """Plan the routing process along with quries generation if retriver node is choosen"""
    user_message = state.get("user_message")
    with logger.span("Planner node execution", user_message=user_message):
        try:
            logger.info("Planning route for user query", user_message=user_message)
            conversation_history = state.get("messages")
            chain = PLANNER_PROMPT | llm.with_structured_output(PlannerStructure)

            res = await chain.ainvoke(input={"conversation_history": conversation_history, "user_message": user_message})

            # res is the pydantic class
            route_to = getattr(res, "route_to", "responder")
            queries = getattr(res, "queries", None)

            logger.info("Planner decision completed", route_to=route_to, queries=queries)
            return {"route_to": route_to, "queries": queries}
        except Exception as e:
            logger.error("Planner node execution failed", error=str(e))
            raise MyException(e, sys)