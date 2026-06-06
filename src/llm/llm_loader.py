from langchain_groq import ChatGroq
from src.constants import MODEL_NAME
import logging
llm = ChatGroq(
    model=MODEL_NAME
)
logging.info(f"LLM initialized with model_name:{MODEL_NAME}")