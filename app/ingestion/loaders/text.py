
from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from typing import Iterator,List
from app.core.exception import MyException
import sys



class TextLoader(BaseLoader):
    def __init__(self,file_path:str):
        self.file_path = file_path
        

    def lazy_load(self)->Iterator[Document]:
        """A lazy loader that yields documents page by page."""
        try:

            f= open(file=self.file_path,encoding="utf-8",errors="ignore")
            yield Document(page_content=f.read(),metadata={"source":self.file_path,"page":0})

        except Exception as e:
            raise MyException(e,sys)

        finally:
            f.close()


    def load(self)->List[Document]:
        """Load all documents into memory at once."""

        try:
            return list(self.lazy_load())

        except Exception as e:
            raise MyException(e,sys)

   

async def text_loader(file_path:str):
    try:

        loader = TextLoader(file_path=file_path)

        return await loader.aload()

    except Exception as e:
        raise MyException(e,sys)



