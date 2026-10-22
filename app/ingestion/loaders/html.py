
from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from typing import Iterator,List
from app.core.exception import MyException
from app.core.logger import logger
import sys

from bs4 import BeautifulSoup


# NOTE langchain aload automatically wraps and runs the fn lazy_load in .to_thread() which makes it non-blocking

class HTMLLoader(BaseLoader):
    def __init__(self,file_path:str):
        self.file_path = file_path
        

    def lazy_load(self)->Iterator[Document]:
        """A lazy loader that yields documents page by page."""
        logger.info("Starting HTML lazy load", file_path=self.file_path)
        try:
            f = open(file=self.file_path,encoding="utf-8",errors="ignore")
            content = f.read()
            logger.debug("HTML file read", file_path=self.file_path, raw_size=len(content))

            soup = BeautifulSoup(content,"html.parser")
            # 1. Remove Junk (Scripts, Styles, Metadata)
            for script in soup(["script", "style", "meta", "noscript"]):
                script.decompose()

            # 2. Extract Text
            text = soup.get_text(separator="\n")

            # 3. Clean Whitespace (Collapse multiple newlines)
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_clean = '\n'.join(chunk for chunk in chunks if chunk)

            logger.info("HTML parsed and cleaned", file_path=self.file_path, clean_size=len(text_clean))
            yield Document(page_content=text_clean,metadata={"source":self.file_path,"page":0})

        except Exception as e:
            logger.error("Failed to lazy load HTML", file_path=self.file_path, error=str(e))
            raise MyException(e,sys)

        finally:
            f.close()


    def load(self)->List[Document]:
        """Load all documents into memory at once."""
        logger.info("Loading HTML into memory", file_path=self.file_path)
        try:
            docs = list(self.lazy_load())
            logger.info("HTML load complete", file_path=self.file_path, doc_count=len(docs))
            return docs

        except Exception as e:
            logger.error("Failed to load HTML", file_path=self.file_path, error=str(e))
            raise MyException(e,sys)



async def html_loader(file_path:str):
    logger.info("html_loader called", file_path=file_path)
    try:
        loader = HTMLLoader(file_path=file_path)
        docs = await loader.aload()
        logger.info("html_loader finished", file_path=file_path, doc_count=len(docs))
        return docs

    except Exception as e:
        logger.error("html_loader failed", file_path=file_path, error=str(e))
        raise MyException(e,sys)



