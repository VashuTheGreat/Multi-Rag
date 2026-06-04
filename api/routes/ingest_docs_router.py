from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import logging
from api.constants import PUBLIC_FOLDER_FILE_PATH
import os

from src.pipeline.Vectiorizer_pipeline import VectiorizerPipeline
from src.entity.config_entity import (
    DataIngestionConfig, 
    ContentEmbedderConfig, 
    DataTransformationConfig, 
    ContentTransformationConfig
)

from src.constants import ARTIFACT_DIR, INGESTION_FOLDER_NAME, TRANSFORMATION_FOLDER_NAME

router = APIRouter()

@router.get("/", tags=['File'])
async def ingest_docs(request: Request):
    try:
        user = request.scope.get("user")
        if not user:
            return JSONResponse({"error": "pls login"}, status_code=401)
        
        thread_id = user.thread_id
        folder_path = os.path.join(PUBLIC_FOLDER_FILE_PATH, thread_id)
        
        if not os.path.exists(folder_path):
            return JSONResponse({"error": "No files found for this user"}, status_code=404)

        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if not files:
            return JSONResponse({"error": "No files to ingest"}, status_code=400)

        ingestion_configs = [
            DataIngestionConfig(
                input_file_path=os.path.join(folder_path, file_name),
                save_file_path=f"{ARTIFACT_DIR}/{thread_id}/{INGESTION_FOLDER_NAME}/{file_name}.pdf"
            )
            for file_name in files
        ]

        content_embedder_config = ContentEmbedderConfig(data_ingestion_configs=ingestion_configs)
        
        transformation_configs = [
            DataTransformationConfig(vector_store_path=f"{ARTIFACT_DIR}/{thread_id}/{TRANSFORMATION_FOLDER_NAME}/{file_name}")
            for file_name in files
        ]
        
        content_transformation_config = ContentTransformationConfig(data_transformation_configs=transformation_configs)

        vectorizer_pipeline = VectiorizerPipeline(
            content_embedder_config=content_embedder_config,
            content_transformation_config=content_transformation_config
        )

        result = await vectorizer_pipeline.initiate(thread_id=thread_id)
        logging.info(f"Vectorizer Pipeline Result: {result}")

        return JSONResponse(
            content={
                "message": "Ingestion completed successfully",
                "files_processed": len(files)
            },
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error during ingestion: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)