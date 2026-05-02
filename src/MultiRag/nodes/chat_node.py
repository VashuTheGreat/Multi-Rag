import logging
import json
import re
from src.MultiRag.models.rag_model import State
from utils.asyncHandler import asyncHandler
from src.MultiRag.llm.llm_loader import llm
from src.MultiRag.prompts.prompt_templates import CHAT_PROMPT
from langchain_core.messages import SystemMessage, AIMessage
from src.MultiRag.tools.web_search import WebSearch

web_search_tool = WebSearch().search



@asyncHandler
async def chat_node(state: State):
    logging.info("Executing chat node...")
    logging.info(f"Binding chat LLM with web search tool")

    tool_limit_hit=state.get("jump_to") == "end"

    if tool_limit_hit:
        logging.info("Tool call limit hit, invoking llm without tools")
        chat_llm = llm
    else:
        chat_llm = llm.bind_tools([web_search_tool])
    prompt = [SystemMessage(content=CHAT_PROMPT)] + state.get('messages', [])
    logging.info("Invoking chat LLM...")
    res = await chat_llm.ainvoke(prompt)
  

    logging.info(f"Response retrieved from chat_llm: {res.content if res.content else 'Tool Call'}")
    return {"messages": [res]}
