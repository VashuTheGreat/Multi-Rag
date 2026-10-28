from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    stream: bool = Field(True,description="for allowing streaming")
    metadata: dict = Field(default_factory=dict, description="Optional metadata dictionary")
