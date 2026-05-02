import os
import sys
import asyncio
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()
from logger import *
import logging

from src.MultiRag.pipeline.run_pipeline import RunPipeline


from src.MultiRag.models.rag_model import Content
from src.MultiRag.components.content_embedder import ContentEmbedder
from src.MultiRag.entity.config_entity import ContentEmbedderConfig
import os

# ============= generating retreivers ===========================

async def generate_retreivers(thread_id):
    for file in os.listdir("docs"):
        logging.info(f"Processing file: {file}")
    
        content_embedder_config = ContentEmbedderConfig(
            file_path=f"docs/{file}",
            vector_store_path=f"db/{thread_id}/{file}",  # Updated path structure
        )
        component = ContentEmbedder(content_embedder_config=content_embedder_config)
        retreiver = await component.embed_content()
        logging.info(f"Generated retreiver for {file}: {retreiver}")


# ============= testing pdf query loading =======================
async def pdf_test():

    run_pipeline = RunPipeline()
    
    # Mocking user uploaded files
    temp_user_content = [
        Content(
            name="AI_Intro.pdf",
            about="An introductory document about Artificial Intelligence and Machine Learning.",
            path="docs/AI_Intro.pdf"
        )
    ]

    res = await run_pipeline.initiate(
        thread_id="1", 
        query="What does the AI_Intro.pdf say about Neural Networks? Use the pdf",
        userContent=temp_user_content
    )

    logging.info(f"Final Pipeline Response: {res}")

# ============= testing txt query loading =======================
async def txt_test():
    run_pipeline = RunPipeline()
    
    # Mocking user uploaded files
    temp_user_content = [
        Content(
            name="growing_ai_tools.txt",
            about="General notes about growing AI tools.",
            path="docs/growing_ai_tools.txt"
        )
    ]

    res = await run_pipeline.initiate(
        thread_id="1", 
        query="What does the growing_ai_tools.txt say about AI tools? use the txt file",
        userContent=temp_user_content
    )

    logging.info(f"Final Pipeline Response: {res}")


# ============= testing docs query loading =======================
async def docx_test():
    run_pipeline = RunPipeline()
    
    # Mocking user uploaded files
    temp_user_content = [
        Content(
            name="google.docx",
            about="General notes about company Google.",
            path="docs/google.docx"
        )
    ]

    res = await run_pipeline.initiate(
        thread_id="1", 
        query="What does the google.docx say about Google? use the docx file",
        userContent=temp_user_content
    )

    logging.info(f"Final Pipeline Response: {res}")


# ============= testing image query loading =======================
async def image_test():
    run_pipeline = RunPipeline()
    
    # Mocking user uploaded files
    temp_user_content = [
        Content(
            name="lena.png",
            about="An image of a girl.",
            path="docs/lena.png"
        )
    ]

    res = await run_pipeline.initiate(
        thread_id="1", 
        query="What does the lena.png say about the girl? use the image file",
        userContent=temp_user_content
    )

    logging.info(f"Final Pipeline Response: {res}")




# ============== Running all the tests =============================
async def main():
    logging.info("Starting generating retreivers...")
    await generate_retreivers(thread_id="1")
    logging.info("Retreivers generated successfully. Starting pipeline tests...")
    logging.info("Starting pipeline tests...")
    await pdf_test()
    await txt_test()
    await docx_test()
    await image_test()
    logging.info("Pipeline tests completed.")


asyncio.run(main())