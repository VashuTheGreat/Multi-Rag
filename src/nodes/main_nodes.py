import json
import asyncio
import logging
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document
from langgraph.types import RunnableConfig

from src.llm.llm_loader import llm
from src.tools import WebSearch
from src.utils.asyncHandler import asyncHandler

from src.entity.config_entity import RetreiverConfig, DataIngestionConfig, DataTransformationConfig
from src.retrievers.create_retreivers import Retreiver

from src.states.Main_State import (
    State,
    Orchastrator_output,
    Query_generation_output,
    Relevance_output,
    WebSearchOutput
)

from src.prompts.prompt_templates import (
    ORCHESTRATOR_PROMPT,
    QUERY_GENERATION_PROMPT,
    RELEVANCE_CHECKER_PROMPT,
    WEB_SEARCH_PROMPT,
    CHAT_PROMPT
)

web_search_tool = WebSearch()





@asyncHandler
async def orchastrator_node(state: State) -> dict:
    logging.info("Orchestrator node started")

    structured_llm = llm.with_structured_output(Orchastrator_output)

    has_uploaded_file = state.get("has_uploaded_file", False)
    upload_status = "ALREADY UPLOADED" if has_uploaded_file else "NOT UPLOADED ANY"

    prompt = ORCHESTRATOR_PROMPT.invoke({
        "upload_status": upload_status,
        "messages": state.get("messages", [])
    })

    result = structured_llm.invoke(prompt)

    # Force require_db_search to False if no files have been uploaded
    require_db_search = result.require_db_search if has_uploaded_file else False

    logging.info(
        f"Orchestrator routing decision: require_db_search={require_db_search}"
    )

    return {
        "require_db_search": require_db_search
    }


@asyncHandler
async def query_generation_node(state: State) -> dict:
    logging.info("Query generation node started")

    structured_llm = llm.with_structured_output(Query_generation_output)

    prompt = QUERY_GENERATION_PROMPT.invoke({
        "messages": state.get("messages", [])
    })

    result = structured_llm.invoke(prompt)

    logging.info(
        f"Generated {len(result.queries)} queries"
    )

    return {
        "queries": result.queries
    }


@asyncHandler
async def retreiver_node(state: State) -> dict:
    logging.info("Retriever node started")

    config = RetreiverConfig()
    retriever_obj = Retreiver(retreiver_config=config)

    vector_store_path = state.get("vector_store_file_path")

    if not vector_store_path:
        logging.warning("No vector_store_file_path available for retrieval")
        return {"retreived_results": []}

    retriever_chain = await retriever_obj.create_retreiver(
        vectorstore_file_path=vector_store_path
    )

    if not retriever_chain:
        logging.warning("No retriever chain available")
        return {"retreived_results": []}

    queries = state.get("queries", [])

    if not queries:
        logging.warning("No queries available for retrieval")
        return {"retreived_results": []}

    # Execute retrieve for each query based on whether it's an async retriever or sync.
    # We will assume ainvoke is supported for Langchain BaseRetriever types
    # and aquery or similar for LlamaIndex if it's a query engine.
    # LlamaIndex load_retriever returns as_query_engine() which has aquery()

    results = []

    if hasattr(retriever_chain, "ainvoke"):
        # Langchain retriever
        tasks = [retriever_chain.ainvoke(query) for query in queries]
        results_list = await asyncio.gather(*tasks)
        for res in results_list:
            results.extend(res)
    elif hasattr(retriever_chain, "aquery"):
        # LlamaIndex query engine
        tasks = [retriever_chain.aquery(query) for query in queries]
        results_list = await asyncio.gather(*tasks)
        for res in results_list:
            # LlamaIndex query engine results have source_nodes
            if hasattr(res, "source_nodes"):
                results.extend(res.source_nodes)
            else:
                results.append(res)
    else:
        logging.warning("Retriever chain type not supported for async execution.")

    logging.info(
        f"Retriever returned {len(results)} total document hits across queries"
    )

    return {
        "retreived_results": results
    }



@asyncHandler
async def document_normaliser_node(state: State) -> dict:
    logging.info("Document normaliser node started")

    raw_results = state.get("retreived_results", [])
    normalised_docs = []

    for item in raw_results:
        # 1. Already a Langchain Document
        if isinstance(item, Document):
            normalised_docs.append(item)

        # 2. LlamaIndex NodeWithScore (has .node)
        elif hasattr(item, "node") and hasattr(item.node, "text"):
            metadata = item.node.metadata if hasattr(item.node, "metadata") else {}
            doc = Document(page_content=item.node.text, metadata=metadata)
            if hasattr(item, "score") and item.score is not None:
                doc.metadata["relevance_score"] = float(item.score)
            normalised_docs.append(doc)

        # 3. LlamaIndex BaseNode / Document directly (has .text)
        elif hasattr(item, "text"):
            metadata = item.metadata if hasattr(item, "metadata") else {}
            normalised_docs.append(Document(page_content=item.text, metadata=metadata))

        # 4. Dictionary fallback
        elif isinstance(item, dict):
            page_content = item.get("page_content", item.get("text", ""))
            metadata = item.get("metadata", {})
            normalised_docs.append(Document(page_content=page_content, metadata=metadata))

        # 5. Last resort string cast
        else:
            normalised_docs.append(Document(page_content=str(item), metadata={}))

    logging.info(f"Normalised {len(normalised_docs)} documents to Langchain format")

    return {
        "retreived_results": normalised_docs
    }


@asyncHandler
async def is_retreived_data_enough(state: State) -> dict:
    logging.info("Relevance checker node started")

    retrieved_docs = state.get("retreived_results", [])

    docs_content = "\n\n".join([
        doc.page_content for doc in retrieved_docs
    ]) if retrieved_docs else "No documents retrieved."

    user_query = state.get("messages", [])[-1].content

    prompt = RELEVANCE_CHECKER_PROMPT.invoke({
        "user_query": user_query,
        "retrieved_docs_content": docs_content
    })

    structured_llm = llm.with_structured_output(
        Relevance_output
    )

    result = structured_llm.invoke(prompt)

    logging.info(
        f"Relevance decision: {result.relevance}"
    )

    return {
        "relevance": result.relevance
    }


@asyncHandler
async def web_search_node(state: State) -> dict:
    logging.info("Web search node started")

    query = state.get("messages", [])[-1].content

    structured_llm = llm.with_structured_output(
        WebSearchOutput
    )

    prompt = WEB_SEARCH_PROMPT.invoke({
        "query": query
    })

    generated_queries = structured_llm.invoke(prompt)

    search_tasks = [
        web_search_tool.search.ainvoke(q)
        for q in generated_queries.queries
    ]

    raw_results = await asyncio.gather(*search_tasks)

    results = [
        item
        for sublist in raw_results
        for item in (sublist if isinstance(sublist, list) else [sublist])
    ]

    logging.info(
        f"Web search returned {len(results)} results"
    )

    return {
        "web_search_results": results
    }





@asyncHandler
async def document_refiner(state: State) -> dict:
    logging.info("Document refiner node started")
    return {}

@asyncHandler
async def get_chat_node_content(state: State) -> dict:
    logging.info("Context builder node started")
    return {}

@asyncHandler
async def chat_node(state: State) -> dict:
    logging.info("Chat node started")

    docs_context = state.get("retreived_results", [])

    if docs_context:
        context_status = "Available"
        formatted_context = "\n\n".join([
            f"Source: {doc.metadata.get('source', 'Unknown')}\nContent: {doc.page_content}"
            for doc in docs_context
        ])
    else:
        context_status = "Not available"
        formatted_context = "No retrieved documents."

    prompt = CHAT_PROMPT.invoke({
        "context_status": context_status,
        "docs_context": formatted_context,
        "messages": state.get("messages", [])
    })

    response = llm.invoke(prompt)

    logging.info("Final response generated")

    return {
        "messages": [response],
        "ai_response": response.content
    }