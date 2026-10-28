from langchain_groq import ChatGroq
from functools import lru_cache
from src.app_config import get_app_config


app_config = get_app_config()

@lru_cache
def get_llm(model="openai/gpt-oss-120b"):
    llm = ChatGroq(model=model,api_key=app_config.groq_api_key)
    return llm