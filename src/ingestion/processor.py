from src.ingestion.loaders import html, office, pdf, text
from src.ingestion.chunking.splitter import split
from src.service import vector_store as vector_store_module
from src.service.vector_store import get_vector_store, get_client
from src.core.logger import logger
from src.core.exception import MyException
import os
import sys


client = get_client()


def map_file_type(file_path: str):
    ext = file_path.split(".")[-1].lower() if "." in file_path else ""
    logger.debug("Mapping file extension", file_path=file_path, extension=ext)
    match ext:
        case "pdf":
            return pdf.pdf_loader
        case "txt":
            return text.text_loader
        case "html" | "htm":
            return html.html_loader
        case "docx" | "doc" | "ppt" | "pptx" | "word":
            return office.office_loader
        case _:
            return text.text_loader


async def process_file(file_path: str = "data/text.txt"):
    with logger.span("Ingestion pipeline: {file_path}", file_path=file_path):
        try:
            logger.info("Starting file processing", file_path=file_path)
            loader = map_file_type(file_path=file_path)
            documents = await loader(file_path=file_path)
            logger.info("Loaded raw documents", file_path=file_path, count=len(documents))

            documents = split(documents)
            logger.info("Documents split into chunks", file_path=file_path, chunk_count=len(documents))

            vs_client = vector_store_module.get_client()
            result = await vs_client.upsert(documents)
            logger.info("File processing and upsert complete", file_path=file_path)
            return result if result is not None else True

        except Exception as e:
            logger.error("Failed to process file", file_path=file_path, error=str(e))
            raise MyException(e, sys)


async def process_folder(folder_path: str = "data"):
    with logger.span("Ingesting folder: {folder_path}", folder_path=folder_path):
        try:
            logger.info("Traversing folder", folder_path=folder_path)
            results = []
            for root, _, files in os.walk(folder_path):
                for file in sorted(files):
                    file_path = os.path.join(root, file)
                    res = await process_file(file_path=file_path)
                    results.append(res)
            logger.info("Folder processing complete", folder_path=folder_path, processed_files=len(results))
            return results

        except Exception as e:
            logger.error("Failed to process folder", folder_path=folder_path, error=str(e))
            raise MyException(e, sys)
