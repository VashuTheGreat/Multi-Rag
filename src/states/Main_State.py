from typing import Any, List, Literal, Optional

from langgraph.graph.message import MessagesState
from pydantic import BaseModel


class State(MessagesState):
    file_paths: Optional[List[str]]
    has_uploaded_file: bool = False

    require_db_search: bool

    queries: List[str]

    retreived_results: List[Any]


    relevance: Literal[
        "CORRECT",
        "AMBIGUOUS",
        "INCORRECT"
    ]

    web_search_results: List[Any]


    ai_response: str


class Orchastrator_output(BaseModel):
    require_db_search: bool


class Query_generation_output(BaseModel):
    queries: List[str]


class Relevance_output(BaseModel):
    relevance: Literal[
        "CORRECT",
        "AMBIGUOUS",
        "INCORRECT"
    ]


class WebSearchOutput(BaseModel):
    queries: List[str]