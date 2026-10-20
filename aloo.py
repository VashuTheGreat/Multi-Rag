import asyncio
import sys
import os
sys.path.append(os.getcwd())
import glob
from src.entity.config_entity import ContentEmbedderConfig, DataIngestionConfig, ContentTransformationConfig, DataTransformationConfig
from src.pipeline.Vectiorizer_pipeline import VectiorizerPipeline

# Ensure dot env is loaded so configs like LLAMA_CLOUD_API_KEY can be parsed properly
from dotenv import load_dotenv
load_dotenv()

async def main():
    thread_id = "1"

    # Get all files from data folder
    data_files = glob.glob("data/*")

    if not data_files:
        print("No files found in data/ folder")
        return

    print(f"Found files for ingestion: {data_files}")

    # Prepare ingestion configs
    ingestion_configs = []
    transformation_configs = []

    # The unified vector store path for this user/thread
    vector_store_path = os.path.join("artifacts", thread_id, "vector_store")

    for file_path in data_files:
        if not os.path.isfile(file_path):
            continue

        ingestion_configs.append(
            DataIngestionConfig(
                input_file_path=file_path,
                save_file_path=os.path.join("artifacts", thread_id, "ingested_files", os.path.basename(file_path))
            )
        )
        transformation_configs.append(
            DataTransformationConfig(
                vector_store_path=vector_store_path
            )
        )

    embedder_config = ContentEmbedderConfig(data_ingestion_configs=ingestion_configs)
    transformation_config = ContentTransformationConfig(data_transformation_configs=transformation_configs)

    # Initialize the pipeline
    pipeline = VectiorizerPipeline(
        content_embedder_config=embedder_config,
        content_transformation_config=transformation_config
    )

    print(f"\n[+] Starting VectorizerPipeline for thread '{thread_id}'...")
    try:
        result = await pipeline.initiate(thread_id=thread_id)

        print("\n[+] Pipeline completed successfully.")
        if result and result.data_transformation_artifacts:
            # We just print the first one since all point to the same vector store
            print(f"[+] Final Vector store path: {result.data_transformation_artifacts[0].vector_store_path}")
            print(f"[+] Files embedded in vector store: {len(result.data_transformation_artifacts)}")
    except Exception as e:
        print(f"\n[-] Pipeline failed with error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
