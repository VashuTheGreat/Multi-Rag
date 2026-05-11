import os
import sys
import asyncio
sys.path.append(os.getcwd())

import logging
import pytest
from dotenv import load_dotenv
from logger import *

from src.MultiRag.pipeline.run_pipeline import RunPipeline
from src.MultiRag.models.rag_model import Content
from src.MultiRag.components.content_embedder import ContentEmbedder
from src.MultiRag.entity.config_entity import ContentEmbedderConfig

load_dotenv()

THREAD_ID = "1"


@pytest.fixture(scope="session", autouse=True)
def generate_retreivers():
    async def _generate():
        for file in os.listdir("docs"):
            logging.info(f"Processing file: {file}")
            content_embedder_config = ContentEmbedderConfig(
                file_path=f"docs/{file}",
                vector_store_path=f"db/{THREAD_ID}/{file}",
            )
            component = ContentEmbedder(content_embedder_config=content_embedder_config)
            retreiver = await component.embed_content()
            logging.info(f"Generated retreiver for {file}: {retreiver}")

    asyncio.run(_generate())


def test_pdf_query():
    async def _run():
        run_pipeline = RunPipeline()
        temp_user_content = [
            Content(
                name="AI_Intro.pdf",
                about="An introductory document about Artificial Intelligence and Machine Learning.",
                path="docs/AI_Intro.pdf"
            )
        ]
        res = await run_pipeline.initiate(
            thread_id=THREAD_ID,
            query="What does the AI_Intro.pdf say about Neural Networks? Use the pdf",
            userContent=temp_user_content
        )
        logging.info(f"Final Pipeline Response: {res}")
        return res

    result = asyncio.run(_run())
    assert result is not None


def test_txt_query():
    async def _run():
        run_pipeline = RunPipeline()
        temp_user_content = [
            Content(
                name="growing_ai_tools.txt",
                about="General notes about growing AI tools.",
                path="docs/growing_ai_tools.txt"
            )
        ]
        res = await run_pipeline.initiate(
            thread_id=THREAD_ID,
            query="What does the growing_ai_tools.txt say about AI tools? use the txt file",
            userContent=temp_user_content
        )
        logging.info(f"Final Pipeline Response: {res}")
        return res

    result = asyncio.run(_run())
    assert result is not None


def test_docx_query():
    async def _run():
        run_pipeline = RunPipeline()
        temp_user_content = [
            Content(
                name="google.docx",
                about="General notes about company Google.",
                path="docs/google.docx"
            )
        ]
        res = await run_pipeline.initiate(
            thread_id=THREAD_ID,
            query="What does the google.docx say about Google? use the docx file",
            userContent=temp_user_content
        )
        logging.info(f"Final Pipeline Response: {res}")
        return res

    result = asyncio.run(_run())
    assert result is not None


def test_image_query():
    async def _run():
        run_pipeline = RunPipeline()
        temp_user_content = [
            Content(
                name="lena.png",
                about="An image of a girl.",
                path="docs/lena.png"
            )
        ]
        res = await run_pipeline.initiate(
            thread_id=THREAD_ID,
            query="What does the lena.png say about the girl? use the image file",
            userContent=temp_user_content
        )
        logging.info(f"Final Pipeline Response: {res}")
        return res

    result = asyncio.run(_run())
    assert result is not None
