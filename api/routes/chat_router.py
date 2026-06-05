from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import logging
import os

from api.states.chat_state import ChatRequest
from src.pipeline.GraphRunner_pipeline import RunGraphPipeline
from langchain_core.messages import HumanMessage
from src.constants import ARTIFACT_DIR, TRANSFORMATION_FOLDER_NAME

router = APIRouter()

@router.post("", tags=['Chat'])
async def chat_endpoint(request: Request, chat_request: ChatRequest):
    try:
        user = request.scope.get("user")
        if not user:
            return JSONResponse(content={"error": "pls login"}, status_code=401)

        thread_id = user.thread_id
        user_artifact_dir = os.path.join(ARTIFACT_DIR, thread_id)
        if not os.path.exists(user_artifact_dir):
            return JSONResponse(content={"error": "first ingest the data and then chat"}, status_code=400)

        vector_store_base = os.path.join(user_artifact_dir, TRANSFORMATION_FOLDER_NAME)
        if not os.path.exists(vector_store_base):
            return JSONResponse(content={"error": "first ingest the data and then chat"}, status_code=400)

        vector_store_paths = []
        for d in os.listdir(vector_store_base):
            path = os.path.join(vector_store_base, d)
            if os.path.isdir(path):
                vector_store_paths.append(path)

        if not vector_store_paths:
            return JSONResponse(content={"error": "no vector stores found, please ingest data"}, status_code=400)

        initial_state = {
            "messages": [HumanMessage(content=chat_request.message)],
            "vector_store_file_paths": vector_store_paths,
            "queries": [],
            "retreived_results": [],
            "ai_response": ""
        }

        graph_pipeline = RunGraphPipeline()
        graph_result = await graph_pipeline.run_graph(initial_state, config={"configurable": {"thread_id": thread_id}})
        logging.info(f"Graph execution result: {graph_result}")

        return JSONResponse(
            content={
                "response": graph_result.get("ai_response", "No response generated"),
                "user": user.dict()
            },
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error during chat: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
