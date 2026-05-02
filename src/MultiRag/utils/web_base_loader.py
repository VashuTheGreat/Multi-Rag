

from langchain_community.document_loaders import WebBaseLoader
import logging
from exception import MyException
import sys

async def load_web_content(url: str) -> str:
    try:
        logging.info(f"Loading web content from URL: {url}")
        content = WebBaseLoader(url).load()
        logging.info(f"Successfully loaded content from URL: {url}")
        return content
    except Exception as e:
        logging.error(f"Error loading web content from URL: {url} - {str(e)}")
        raise MyException(f"Error loading web content from URL: {url} - {str(e)}", sys)
   