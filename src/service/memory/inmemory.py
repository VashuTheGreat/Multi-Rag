from langgraph.checkpoint.memory import InMemorySaver
from functools import lru_cache

@lru_cache
def get_memory():
    return InMemorySaver()