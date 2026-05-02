import os

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from utils.asyncHandler import asyncHandler
from src.MultiRag.constants import EMBEDDING_MODEL
from src.MultiRag.constants import EXCEPTED_FILE_TYPE, RETREIVER_DEFAULT_K
import logging

# ---------------- Embedding Model ----------------
class CompatibleEmbeddings(HuggingFaceEmbeddings):
    def __call__(self, text: str):
        return self.embed_query(text)

embedding_model = CompatibleEmbeddings(model=EMBEDDING_MODEL)

# ---------------- Document Fetcher ----------------
@asyncHandler
async def document_fetcher(docs: str = "data"):
    logging.info(f"Fetching docs from {docs}")

    if not os.path.exists(docs):
        logging.error(f"Docs folder not found at: {docs}")
        raise FileNotFoundError(f"Docs folder not found at: {docs}")

    if os.path.isfile(docs):
        files = [os.path.basename(docs)]
        docs = os.path.dirname(docs) or "."
    else:
        files = os.listdir(docs)

    from langchain_community.document_loaders import TextLoader, PyPDFLoader

    documents = []
    for file in files:
        file_path = os.path.join(docs, file)
        ext = file.split(".")[-1].lower()

        try:
            if ext == "txt":
                loader = TextLoader(file_path, encoding="utf-8")
                documents.extend(loader.load())

            elif ext == "pdf":
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())

            elif ext == "docx":
                from langchain_community.document_loaders import Docx2txtLoader
                loader = Docx2txtLoader(file_path)
                documents.extend(loader.load())

            elif ext in ["png", "jpg", "jpeg"]:
                from langchain_community.document_loaders import UnstructuredImageLoader
                loader = UnstructuredImageLoader(file_path)
                documents.extend(loader.load())

        except Exception as e:
            logging.error(f"Failed to load {file_path}: {e}")

    return documents


# ---------------- Chunking ----------------
@asyncHandler
async def chunking_documents(documents, chunk_size: int = 200, chunk_overlap: int = 0):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_documents(documents)


# ---------------- FAISS Vector Store ----------------
@asyncHandler
async def create_vector_store(path: str = "db", docs: str = "data"):

    if os.path.exists(path):
        logging.info("Existing FAISS DB found. Loading...")
        vectorstore = FAISS.load_local(path, embedding_model, allow_dangerous_deserialization=True)
        return vectorstore

    logging.info("Creating new FAISS DB...")
    documents = await document_fetcher(docs=docs)
    if not documents:
        logging.warning(f"No documents found or failed to load any documents from {docs}. Skipping FAISS creation.")
        return None
        
    chunks = await chunking_documents(documents)
    if not chunks:
        logging.warning(f"No chunks created from documents in {docs}. Skipping FAISS creation.")
        return None

    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embedding_model
    )

    # Save locally
    vectorstore.save_local(path)

    return vectorstore


# ---------------- Retriever ----------------
@asyncHandler
async def create_retreiver(vectorstore, k: int = RETREIVER_DEFAULT_K):
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    return retriever


# ---------------- Get Raw Documents ----------------
async def get_documents(docs: str = "data") -> str:
    documents = await document_fetcher(docs=docs)
    text = "\n".join([doc.page_content for doc in documents])
    return text