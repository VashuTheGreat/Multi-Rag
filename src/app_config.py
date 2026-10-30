from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List, Optional, Union
from pydantic import Field

class AppConfig(BaseSettings):
    groq_api_key: Optional[str] = Field(None, validation_alias="GROQ_API_KEY")
    llama_cloud_api_key: Optional[str] = Field(None, validation_alias="LLAMA_CLOUD_API_KEY")
    port: Union[int, str] = Field(7860, validation_alias="PORT")
    qdrant_api_key: Optional[str] = Field(None, validation_alias="QDRANT_API_KEY")
    qdrant_cluster_endpoint: Optional[str] = Field(None, validation_alias="QDRANT_CLUSTER_ENDPOINT")
    collection_name: Optional[str] = Field(None, validation_alias="COLLECTION_NAME")
    service_name: Optional[str] = Field(None, validation_alias="SERVICE_NAME")
    embedding_model: Optional[str] = Field(None, validation_alias="EMBEDDING_MODEL")
    embedding_dim: Optional[Union[int, str]] = Field(None, validation_alias="EMBEDDING_DIM")
    pydantic_logfire_api_key: Optional[str] = Field(None, validation_alias="PYDANTIC_LOGFIRE_API_KEY")
    ingestion_password: str = Field("aloo", validation_alias="INGESTION_PASSWORD")
    checkpoint_db_path: str = Field("data/checkpoints.db", validation_alias="CHECKPOINT_DB_PATH")


    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )



@lru_cache
def get_app_config():
    return AppConfig()

