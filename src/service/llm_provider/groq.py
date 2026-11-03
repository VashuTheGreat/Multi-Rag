from langchain_groq import ChatGroq
from functools import lru_cache
from src.app_config import get_app_config


app_config = get_app_config()
DEFAULT_MODEL = "openai/gpt-oss-120b"
AVAILABLE_MODELS = frozenset({
    "qwen/qwen3.8-27b",
    "canopylabs/orpheus-arabic-saudi",
    "canopylabs/orpheus-v1-english",
    "meta-llama/llama-prompt-guard-2-22m",
    "meta-llama/llama-prompt-guard-2-86m",
    DEFAULT_MODEL,
    "openai/gpt-oss-20b",
    "openai/gpt-oss-safeguard-20b",
    "whisper-large-v3",
    "whisper-large-v3-turbo",
})

@lru_cache
def get_llm(model: str = DEFAULT_MODEL):
    return ChatGroq(model=model or DEFAULT_MODEL, api_key=app_config.groq_api_key)