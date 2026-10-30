from langchain_core.document_loaders.base import BaseLoader
from unstructured.partition.auto import partition
from langchain_core.documents import Document
from typing import Iterator, List
from src.core.exception import MyException
from src.core.logger import logger
import sys


class OfficeLoader(BaseLoader):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def lazy_load(self) -> Iterator[Document]:
        with logger.span("Lazy loading Office document: {file_path}", file_path=self.file_path):
            try:
                logger.info("Partitioning Office document", file_path=self.file_path)
                elements = partition(filename=self.file_path)
                logger.info("Office document partitioned successfully", file_path=self.file_path, element_count=len(elements))

                for i, e in enumerate(elements):
                    logger.debug("Processing Office element", file_path=self.file_path, element_index=i, element_type=type(e).__name__)
                    yield Document(
                        page_content=e.text,
                        metadata={"source": self.file_path, "page": i},
                    )

                logger.info("Office lazy load complete", file_path=self.file_path, elements_loaded=len(elements))

            except Exception as e:
                logger.error("Failed to lazy load Office file", file_path=self.file_path, error=str(e))
                raise MyException(e, sys)

    def load(self) -> List[Document]:
        with logger.span("Loading Office file into memory: {file_path}", file_path=self.file_path):
            try:
                docs = list(self.lazy_load())
                logger.info("Office document load complete", file_path=self.file_path, doc_count=len(docs))
                return docs

            except Exception as e:
                logger.error("Failed to load Office file", file_path=self.file_path, error=str(e))
                raise MyException(e, sys)


async def office_loader(file_path: str):
    with logger.span("Async Office loader: {file_path}", file_path=file_path):
        try:
            logger.info("Initiating Office document load", file_path=file_path)
            loader = OfficeLoader(file_path=file_path)
            docs = await loader.aload()
            logger.info("Async Office load finished", file_path=file_path, doc_count=len(docs))
            return docs

        except Exception as e:
            logger.error("Async Office loader failed", file_path=file_path, error=str(e))
            raise MyException(e, sys)
