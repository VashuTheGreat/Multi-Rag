import logging
from src.MultiRag.entity.config_entity import ContentEmbedderConfig
from utils.asyncHandler import asyncHandler
from src.MultiRag.models.worker_model import State
from src.MultiRag.components.content_embedder import ContentEmbedder
from src.MultiRag.entity.config_entity import ContentEmbedderConfig
import os

@asyncHandler
async def txt_node(state: State) -> State:
    logging.info("Starting TXT worker node...")
    content_embedder_config = ContentEmbedderConfig(
        file_path=state.file_path,
        vector_store_path=(f"db/{state.thread_id}/{os.path.basename(state.file_path)}"),
    )
    logging.info(f"Created ContentEmbedderConfig: {content_embedder_config}")
    retreiver = await ContentEmbedder(content_embedder_config=content_embedder_config).embed_content()

    if retreiver.retreivar:
        content = await retreiver.retreivar.retreive(state.plan_to_retrieve)
        logging.info("Content embedding completed. Retrieving relevant information... retreived content is %s", content)
    else:
        logging.warning(f"Retriever could not be initialized for {state.file_path}. Skipping retrieval.")
        content = [f"Error: Could not process file {state.file_path}. Ensure dependencies are installed."]

    return {"worker_result": content}
    