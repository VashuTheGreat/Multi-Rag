from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os
import logging
from api.constants import PUBLIC_FOLDER_FILE_PATH
from src.entity.config_entity import DataIngestionConfig, ContentEmbedderConfig, DataTransformationConfig, ContentTransformationConfig
from src.pipeline.DataIngestion_pipeline import DataIngestionPipeline
from src.pipeline.DataTransformation_pipeline import DataTransformationPipeline
from src.constants import ARTIFACT_DIR

router = APIRouter()

@router.get("/ingest", tags=["Ingestion"])
async def ingest_docs(request: Request):
    try:
        user = request.scope.get("user")
        if not user:
            return JSONResponse(content={"error": "pls login"}, status_code=401)

        thread_id = user.thread_id
        user_folder = os.path.join(PUBLIC_FOLDER_FILE_PATH, thread_id)
        
        if not os.path.exists(user_folder):
            return JSONResponse(content={"error": "No files found for this user"}, status_code=404)

        files = [f for f in os.listdir(user_folder) if os.path.isfile(os.path.join(user_folder, f))]
        if not files:
            return JSONResponse(content={"error": "No files to ingest"}, status_code=400)

        user_artifact_base = os.path.join(ARTIFACT_DIR, thread_id)
        
        data_ingestion_configs = []
        data_transformation_configs = []

        for file_name in files:
            input_path = os.path.join(user_folder, file_name)
            
            ingestion_config = DataIngestionConfig(
                input_file_path=input_path,
                save_file_path=os.path.join(user_artifact_base, "ingestion", f"{file_name.split('.')[0]}.pdf")
            )
            data_ingestion_configs.append(ingestion_config)
            
            transformation_config = DataTransformationConfig(
                vector_store_path=os.path.join(user_artifact_base, "transformation", "vector_store", file_name.split('.')[0])
            )
            data_transformation_configs.append(transformation_config)

        embedder_config = ContentEmbedderConfig(data_ingestion_configs=data_ingestion_configs)
        ingestion_pipeline = DataIngestionPipeline(content_embedder_config=embedder_config)
        ingestion_artifact = await ingestion_pipeline.run_pipeline()

        transformation_config_wrapper = ContentTransformationConfig(data_transformation_configs=data_transformation_configs)
        transformation_pipeline = DataTransformationPipeline(
            content_transformation_config=transformation_config_wrapper,
            content_embedder_artifact=ingestion_artifact
        )
        await transformation_pipeline.run_pipeline()

        return JSONResponse(
            content={
                "message": "Ingestion completed successfully",
                "user": request.scope.get("user",None),
                "files_processed": len(files)
            },
            status_code=200
        )

    except Exception as e:
        logging.error(f"Error during ingestion: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
