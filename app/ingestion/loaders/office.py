
from langchain_core.document_loaders.base import BaseLoader
from unstructured.partition.auto import partition
from langchain_core.documents import Document
from typing import Iterator,List
from app.core.exception import MyException
import sys


class OfficeLoader(BaseLoader):
    def __init__(self,file_path:str):
        self.file_path = file_path
        

    def lazy_load(self)->Iterator[Document]:
        """A lazy loader that yields documents page by page."""
        try:
            elements = partition(filename=self.file_path)

            for i,e in enumerate(elements):
                yield Document(
                    page_content=e.text,
                    metadata={"source":self.file_path,"page":i}
                )


        except Exception as e:
            raise MyException(e,sys)

        


    def load(self)->List[Document]:
        """Load all documents into memory at once."""

        try:
            return list(self.lazy_load())

        except Exception as e:
            raise MyException(e,sys)

   

async def office_loader(file_path:str):
    try:

        loader = OfficeLoader(file_path=file_path)

        return await loader.aload()

    except Exception as e:
        raise MyException(e,sys)



