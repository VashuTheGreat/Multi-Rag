from src.ingestion.loaders import pdf,office,html,text
from typing import List
from langchain_core.documents import Document
import pytest
TEST_PDF_PATH="data/tests/pdf.pdf"
TEST_TXT_PATH="data/tests/text.txt"
TEST_HTML_PATH="data/tests/html.html"
TEST_OFFICE_DOCX_PATH="data/tests/docx.docx"
TEST_OFFICE_PPT_PATH="data/tests/ppt.pptx"


@pytest.mark.asyncio
async def test_pdf_loader():
    documents:List[Document]=await pdf.pdf_loader(file_path=TEST_PDF_PATH)
    assert documents!=None
    assert documents[0].page_content!=""



@pytest.mark.asyncio
async def test_text_loader():
    documents:List[Document]=await text.text_loader(file_path=TEST_TXT_PATH)
    assert documents!=None
    assert documents[0].page_content!=""



@pytest.mark.asyncio
async def test_html_loader():
    documents:List[Document]=await html.html_loader(file_path=TEST_HTML_PATH)
    assert documents!=None
    assert documents[0].page_content!=""


@pytest.mark.asyncio
async def test_office_loader():
    """Testing docx"""
    documents:List[Document]=await office.office_loader(file_path=TEST_OFFICE_DOCX_PATH)
    assert documents!=None
    assert documents[0].page_content!=""

    """Testing ppt"""
    documents:List[Document]=await office.office_loader(file_path=TEST_OFFICE_PPT_PATH)
    assert documents!=None
    assert documents[0].page_content!=""