from src.service.llm_provider.groq import get_llm
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage
from ..models.state import AgentState
from ..prompts import RESPONDER_GENERAL_PROMPT, RESPONDER_RETREIVED_PROMPT
from ...core.exception import MyException
from ...core.logger import logger
from langsmith import traceable
import sys

observe = traceable



@observe(name="responder_node", run_type="chain")
async def responder_node(state: AgentState, config: RunnableConfig | None = None):
    """The main node which chats to the user initiate SSE"""
    model = (config or {}).get("configurable", {}).get("model")
    llm = get_llm(model=model)

    conversation_history = state.get("messages")
    user_message = state.get("user_message")
    retreived_content = state.get("retreived_content")

    with logger.span("Responder node execution", has_retrieved_content=bool(retreived_content)):
        try:
            # Seperating out prompts according to the condition (weather there are retreived docs or not)
            if not retreived_content:
                logger.info("Generating response using general knowledge", user_message=user_message)
                chain = RESPONDER_GENERAL_PROMPT | llm
                res = await chain.ainvoke(input={"conversation_history": conversation_history, "user_message": user_message})
                logger.info("General response generated successfully")
                return {"messages": [HumanMessage(content=user_message), res]}

            retreived_content = "".join([(f"{i}. " + getattr(x, "page_content", "") + "\n") for i, x in enumerate(retreived_content)])
            logger.info("Generating response using retrieved context", user_message=user_message, doc_count=len(retreived_content) if isinstance(retreived_content, list) else 1)
            chain = RESPONDER_RETREIVED_PROMPT | llm
            res = await chain.ainvoke(input={"conversation_history": conversation_history, "user_message": user_message, "retreived_content": retreived_content})
            logger.info("Retrieved context response generated successfully")
            return {"messages": [HumanMessage(content=user_message), res]}

        except Exception as e:
            logger.error("Responder node execution failed", error=str(e))
            raise MyException(e, sys)