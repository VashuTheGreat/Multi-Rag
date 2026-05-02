from pydantic import BaseModel
from typing import Optional, Literal, Any, List
from pydantic import Field

class State(BaseModel):
    thread_id: str = "default"
    plan_to_retrieve: str
    file_type: Literal['pdf', 'txt', 'docs', 'docx', 'png', 'url']
    file_path: str=Field(description="Exact file path or URL to retrieve, as specified by the orchestrator")
    worker_result: Optional[List[Any]] = None # output for parent graph