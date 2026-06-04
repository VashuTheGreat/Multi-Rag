import logging
import asyncio
from src.utils.asyncHandler import asyncHandler
from src.states.Main_State import State, Orchastrator_output
from src.prompts.prompt_templates import QUERY_GENERATION_PROMPT as QueryGenerationPrompt, CHAT_PROMPT as ChatNodePrompt
from langchain_core.messages import SystemMessage, HumanMessage
from src.llm.llm_loader import llm
from src.retrievers.create_retreivers import Retreiver
from src.entity.config_entity import RetreiverConfig

@asyncHandler
async def orchastrator_node(state: State) -> dict:
    logging.info("Running orchestrator node")
    llm_ = llm.with_structured_output(Orchastrator_output)
    prompt = [SystemMessage(content=QueryGenerationPrompt)] + state.get("messages", [])
    res = llm_.invoke(prompt)
    logging.info(f"Generated queries: {res.quetries}")
    return {"queries": res.quetries}

@asyncHandler
async def retreiver_node(state: State) -> dict:
    logging.info("Running retriever node")
    config = RetreiverConfig()
    retriever_obj = Retreiver(retreiver_config=config)
    paths = state.get("vector_store_file_paths", [])
    if not paths and state.get("vector_store_file_path"):
        paths = [state["vector_store_file_path"]]
    retriever_chain = await retriever_obj.merge_vector_stores(vector_store_paths=paths)
    if not retriever_chain:
        logging.info("No retriever chain created because of empty or invalid paths")
        return {"retreived_results": []}
    queries = state.get("queries", [])
    if not queries:
        logging.info("No queries generated for retrieval")
        return {"retreived_results": []}
    # we will update thes Queries fetchers using multiple threads
    tasks = [retriever_chain.ainvoke(q) for q in queries]
    results_list = await asyncio.gather(*tasks)
    results = []
    seen_contents = set()
    for query_results in results_list:
        for doc in query_results:
            if doc.page_content not in seen_contents:
                seen_contents.add(doc.page_content)
                if "relevance_score" in doc.metadata:
                    doc.metadata["relevance_score"] = float(doc.metadata["relevance_score"])
                results.append({
                    "page_content": doc.page_content,
                    "metadata": doc.metadata
                })
    logging.info(f"Retrieved {len(results)} results")
    return {"retreived_results": results}

@asyncHandler
async def chat_node(state: State) -> dict:
    logging.info("Running chat node")
    docs = state.get("retreived_results", [])
    context = "\n\n".join([
        doc.get("page_content", "") if isinstance(doc, dict) else getattr(doc, "page_content", "")
        for doc in docs
    ])
    context_msg = SystemMessage(content=f"Retrieved Context:\n{context}")
    prompt = [SystemMessage(content=ChatNodePrompt)] + state.get("messages", []) + [context_msg]
    res = llm.invoke(prompt)
    logging.info("Chat response generated successfully")
    return {"messages": [res], "ai_response": res.content}
