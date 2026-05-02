import logging
from utils.asyncHandler import asyncHandler
from langchain_tavily import TavilySearch
from src.MultiRag.constants import SEARCH_MAX_RESULT, SEARCH_TOPIC
from langchain.tools import tool

# Initialize client globally or inside the tool
tavily_client = TavilySearch(max_results=SEARCH_MAX_RESULT, topic=SEARCH_TOPIC)

@tool
async def web_search(query: str):
    """Use this tool to search the web for relevant information. Input should be a search query string."""
    logging.info(f"Performing web search for query: {query}")
    results = await tavily_client.ainvoke(query)
    return results

class WebSearch:
    def __init__(self):
        self.search = web_search
