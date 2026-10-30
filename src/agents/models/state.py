from typing import Annotated, TypedDict, List, Any
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict, total=False):
    messages: Annotated[List[BaseMessage], operator.add]
    user_message: str
    route_to: str # route on the basis of condition to (eg. respond_node or retreiver_node)
    queries: str | None
    retreived_content: List[Any] | None
    is_blocked: bool
    block_reason: str | None
    ai_response: str | None

    