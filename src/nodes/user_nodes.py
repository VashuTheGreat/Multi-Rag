from src.utils.asyncHandler import asyncHandler
from src.retrievers.create_retreivers import Retreiver
from src.entity.config_entity import RetreiverConfig
import asyncio
import logging
from langchain_core.messages import SystemMessage

@asyncHandler
async def ingestion_node(state, config):
    """This is the ingestion node"""
    logging.info("Ingestion node started")

    
    retreiver_config = RetreiverConfig(
    )


    vectorizer_pipeline = Retreiver(retreiver_config=retreiver_config)
    logging.info("Vectorizer pipeline initialized")

    tasks = [vectorizer_pipeline.ingest(file_path=fp, namespace=config.get("configurable", {}).get("thread_id")) for fp in state.get("file_paths", [])]
    await asyncio.gather(*tasks)

    logging.info("Ingestion node completed")

    return {
        "messages":SystemMessage(content=f"user uploaded a files {', '.join(state.get('file_paths', []))}"),
        "has_uploaded_file": True,
        "file_paths": [] # clear them so next time it doesn't re-ingest
    }
