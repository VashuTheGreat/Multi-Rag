
from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from typing import Iterator,List
from app.core.exception import MyException
import sys

from bs4 import BeautifulSoup

class HTMLLoader(BaseLoader):
    def __init__(self,file_path:str):
        self.file_path = file_path
        

    def lazy_load(self)->Iterator[Document]:
        """A lazy loader that yields documents page by page."""
        try:
            f = open(file=self.file_path,encoding="utf-8",errors="ignore")
            content = f.read()

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
            
            yield Document(page_content=text_clean,metadata={"source":self.file_path,"page":0})
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

   

async def html_loader(file_path:str):
    try:

        loader = HTMLLoader(file_path=file_path)

        return await loader.aload()

    except Exception as e:
        raise MyException(e,sys)



