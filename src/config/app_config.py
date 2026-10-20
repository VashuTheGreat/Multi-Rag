from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List,Optional
from pydantic import Field

class AppConfig(BaseSettings):
    groq_api_key: Optional[str] = Field(None, validation_alias="GROQ_API_KEY")
    llama_cloud_api_key: Optional[str] = Field(None, validation_alias="LLAMA_CLOUD_API_KEY")
    port: Optional[str] = Field(7860, validation_alias="PORT")
    tavily_api_key: Optional[str] = Field(None, validation_alias="TAVILY_API_KEY")
    hf_token: Optional[str] = Field(None, validation_alias="HF_TOKEN")
    pinecone_api_key: Optional[str] = Field(None, validation_alias="PINECONE_API_KEY")
    index_name: Optional[str] = Field(None, validation_alias="INDEX_NAME")

    # app validations
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )



@lru_cache
def app_config():
    return AppConfig()

