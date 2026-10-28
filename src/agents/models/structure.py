from typing import Literal
from pydantic import BaseModel, Field


class PlannerStructure(BaseModel):
    route_to: Literal["responder", "retriever"] = Field(
        default="responder",
        description=(
            "Choose 'responder' if the question can be answered reliably "
            "using general knowledge and conversation history. Choose "
            "'retriever' if answering requires relevant documents, course "
            "materials, or knowledge-base information."
        ),
    )

    queries: str | None = Field(
        default=None,
        description=(
            "A standalone, retrieval-optimized search query that captures "
            "the user's actual information need. Resolve ambiguous references "
            "using conversation history. Required when route_to is 'retriever'; "
            "otherwise, return None."
        ),
    )
