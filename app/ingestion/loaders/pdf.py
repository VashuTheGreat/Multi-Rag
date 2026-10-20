
from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from typing import Iterator,List
import pymupdf
from app.core.exception import MyException
import sys



class PdfLoader(BaseLoader):
    def __init__(self,file_path:str):
        self.file_path = file_path
        

    def lazy_load(self)->Iterator[Document]:
        """A lazy loader that yields documents page by page."""
        try:

            docs = pymupdf.open(self.file_path)

            for i, page in enumerate(docs):
                text = page.get_text().encode("utf8")

                
                yield  Document(
                        page_content=text,
                        metadata={
                            "source":self.file_path,
                            "page":i
                        }
                    )

        except Exception as e:
            raise MyException(e,sys)

        finally:
            docs.close()


    def load(self)->List[Document]:
        """Load all documents into memory at once."""

        try:
            return list(self.lazy_load())

        except Exception as e:
            raise MyException(e,sys)

   

async def pdf_loader(file_path:str):
    try:

        loader = PdfLoader(file_path=file_path)

        return await loader.aload()

    except Exception as e:
        raise MyException(e,sys)



