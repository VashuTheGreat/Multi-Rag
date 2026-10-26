from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from typing import Iterator, List
import pymupdf
from src.core.exception import MyException
from src.core.logger import logger
import sys


class PdfLoader(BaseLoader):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def lazy_load(self) -> Iterator[Document]:
        with logger.span("📄 Lazy loading PDF: {file_path}", file_path=self.file_path):
            docs = None
            try:
                logger.info("📄 Opening PDF file", file_path=self.file_path)
                docs = pymupdf.open(self.file_path)
                page_count = len(docs)
                logger.info("📑 PDF opened successfully", file_path=self.file_path, page_count=page_count)

                for i, page in enumerate(docs):
                    text = page.get_text().encode("utf8")
                    logger.debug("📑 Read PDF page {page}", file_path=self.file_path, page=i, char_count=len(text))
                    yield Document(
                        page_content=text,
                        metadata={
                            "source": self.file_path,
                            "page": i,
                        },
                    )

                logger.info("✅ PDF lazy load complete", file_path=self.file_path, pages_loaded=page_count)

            except Exception as e:
                logger.error("❌ Failed to lazy load PDF", file_path=self.file_path, error=str(e))
                raise MyException(e, sys)

            finally:
                if docs:
                    docs.close()

    def load(self) -> List[Document]:
        with logger.span("📄 Loading PDF into memory: {file_path}", file_path=self.file_path):
            try:
                docs = list(self.lazy_load())
                logger.info("✅ PDF load complete", file_path=self.file_path, doc_count=len(docs))
                return docs

            except Exception as e:
                logger.error("❌ Failed to load PDF", file_path=self.file_path, error=str(e))
                raise MyException(e, sys)


async def pdf_loader(file_path: str):
    with logger.span("🚀 Async PDF loader: {file_path}", file_path=file_path):
        try:
            logger.info("📄 Initiating PDF load", file_path=file_path)
            loader = PdfLoader(file_path=file_path)
            docs = await loader.aload()
            logger.info("✅ Async PDF load finished", file_path=file_path, doc_count=len(docs))
            return docs

        except Exception as e:
            logger.error("❌ Async PDF loader failed", file_path=file_path, error=str(e))
            raise MyException(e, sys)
