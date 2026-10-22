import logfire
from app_config import app_config
from functools import lru_cache


@lru_cache
def initialise_logger():
    config = app_config()
    logfire.configure(
        token=config.pydantic_logfire_api_key,
        service_name="multi-rag",
    )
    logfire.instrument_system_metrics()
    logfire.info("Logfire logger initialised", service="multi-rag")
    return logfire


logger = initialise_logger()