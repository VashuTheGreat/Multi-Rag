# import os
# import sys
# import asyncio
# import logging

# sys.path.append(os.getcwd())
# from dotenv import load_dotenv
# load_dotenv()

# import logger
# import logging

# from src.entity.config_entity import (
#     DataIngestionConfig, 
#     ContentEmbedderConfig, 
#     DataTransformationConfig, 
#     ContentTransformationConfig
# )
# from src.pipeline.Vectiorizer_pipeline import VectiorizerPipeline
# from src.pipeline.GraphRunner_pipeline import RunGraphPipeline

# from langchain_core.messages import HumanMessage
# async def main():
#     thread_id = "123"
#     logging.info("Starting Full Pipeline Integration Test...")
    
#     ingestion_configs = [
#         DataIngestionConfig(
#             input_file_path="/home/vashuthegreat/Projects/Multi-Rag/data/growing_ai_tools.txt",
#             save_file_path=f"artifacts/{thread_id}/ingestion/growing_ai_tools.pdf"
#         ),
#         DataIngestionConfig(
#             input_file_path="/home/vashuthegreat/Projects/Multi-Rag/data/lena.png",
#             save_file_path=f"artifacts/{thread_id}/ingestion/lena.pdf"
#         )
#     ]
#     content_embedder_config = ContentEmbedderConfig(data_ingestion_configs=ingestion_configs)
    
#     transformation_configs = [
#         DataTransformationConfig(vector_store_path=f"artifacts/{thread_id}/transformation/vector_store/growing_ai_tools"),
#         DataTransformationConfig(vector_store_path=f"artifacts/{thread_id}/transformation/vector_store/lena")
#     ]
#     content_transformation_config = ContentTransformationConfig(data_transformation_configs=transformation_configs)

#     vectorizer_pipeline = VectiorizerPipeline(
#         content_embedder_config=content_embedder_config,
#         content_transformation_config=content_transformation_config
#     )

#     result = await vectorizer_pipeline.initiate(thread_id=thread_id)
#     logging.info(f"Vectorizer Pipeline Result: {result}")

#     vector_store_paths = [art.vector_store_path for art in result.data_transformation_artifacts]
    
#     initial_state = {
#         "messages": [HumanMessage(content="What is growing AI tools?")],
#         "vector_store_file_paths": vector_store_paths,
#         "queries": [],
#         "retreived_results": [],
#         "ai_response": ""
#     }
    
#     graph_pipeline = RunGraphPipeline()
#     graph_result = await graph_pipeline.run_graph(initial_state, config={"configurable": {"thread_id": thread_id}})
#     logging.info(f"Graph execution result: {graph_result}")

# if __name__ == "__main__":
#     asyncio.run(main())