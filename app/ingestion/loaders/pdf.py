
from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from typing import Iterator,List
import pymupdf
from app.core.exception import MyException
from app.core.logger import logger
import sys



class PdfLoader(BaseLoader):
    def __init__(self,file_path:str):
        self.file_path = file_path
        

    def lazy_load(self)->Iterator[Document]:
        """A lazy loader that yields documents page by page."""
        logger.info("Starting PDF lazy load", file_path=self.file_path)
        try:
            docs = pymupdf.open(self.file_path)
            page_count = len(docs)
            logger.info("PDF opened successfully", file_path=self.file_path, page_count=page_count)

            for i, page in enumerate(docs):
                text = page.get_text().encode("utf8")
                logger.debug("Loaded PDF page", file_path=self.file_path, page=i, char_count=len(text))
                yield  Document(
                        page_content=text,
                        metadata={
                            "source":self.file_path,
                            "page":i
                        }
                    )

            logger.info("PDF lazy load complete", file_path=self.file_path, pages_loaded=page_count)

        except Exception as e:
            logger.error("Failed to lazy load PDF", file_path=self.file_path, error=str(e))
            raise MyException(e,sys)

        finally:
            docs.close()


    def load(self)->List[Document]:
        """Load all documents into memory at once."""
        logger.info("Loading PDF into memory", file_path=self.file_path)
        try:
            docs = list(self.lazy_load())
            logger.info("PDF load complete", file_path=self.file_path, doc_count=len(docs))
            return docs

        except Exception as e:
            logger.error("Failed to load PDF", file_path=self.file_path, error=str(e))
            raise MyException(e,sys)



async def pdf_loader(file_path:str):
    logger.info("pdf_loader called", file_path=file_path)
    try:
        loader = PdfLoader(file_path=file_path)
        docs = await loader.aload()
        logger.info("pdf_loader finished", file_path=file_path, doc_count=len(docs))
        return docs

    except Exception as e:
        logger.error("pdf_loader failed", file_path=file_path, error=str(e))
        raise MyException(e,sys)



