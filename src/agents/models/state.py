from typing import Annotated, TypedDict, List, Any
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict, total=False):
    messages: Annotated[List[BaseMessage], operator.add]
    user_message: str
    route_to: str
    queries: str | None
    retreived_content: List[Any] | None
    