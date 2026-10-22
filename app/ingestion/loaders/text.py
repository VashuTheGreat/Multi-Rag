
from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from typing import Iterator,List
from app.core.exception import MyException
from app.core.logger import logger
import sys



class TextLoader(BaseLoader):
    def __init__(self,file_path:str):
        self.file_path = file_path
        

    def lazy_load(self)->Iterator[Document]:
        """A lazy loader that yields documents page by page."""
        logger.info("Starting text lazy load", file_path=self.file_path)
        try:
            f= open(file=self.file_path,encoding="utf-8",errors="ignore")
            content = f.read()
            logger.info("Text file read", file_path=self.file_path, char_count=len(content))
            yield Document(page_content=content,metadata={"source":self.file_path,"page":0})

        except Exception as e:
            logger.error("Failed to lazy load text file", file_path=self.file_path, error=str(e))
            raise MyException(e,sys)

        finally:
            f.close()


    def load(self)->List[Document]:
        """Load all documents into memory at once."""
        logger.info("Loading text file into memory", file_path=self.file_path)
        try:
            docs = list(self.lazy_load())
            logger.info("Text load complete", file_path=self.file_path, doc_count=len(docs))
            return docs

        except Exception as e:
            logger.error("Failed to load text file", file_path=self.file_path, error=str(e))
            raise MyException(e,sys)



async def text_loader(file_path:str):
    logger.info("text_loader called", file_path=file_path)
    try:
        loader = TextLoader(file_path=file_path)
        docs = await loader.aload()
        logger.info("text_loader finished", file_path=file_path, doc_count=len(docs))
        return docs

    except Exception as e:
        logger.error("text_loader failed", file_path=file_path, error=str(e))
        raise MyException(e,sys)



