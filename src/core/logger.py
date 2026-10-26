import logfire
from src.app_config import get_app_config
from functools import lru_cache


@lru_cache
def initialise_logger():
    app_config = get_app_config()
    logfire.configure(
        send_to_logfire="if-token-present",
        token=app_config.pydantic_logfire_api_key,
        service_name=app_config.service_name or "multi-rag",
    )
    logfire.instrument_pydantic()
    logfire.instrument_system_metrics()
    logfire.info("🔥 Logfire logger initialised successfully", service=app_config.service_name or "multi-rag")
    return logfire


logger = initialise_logger()
