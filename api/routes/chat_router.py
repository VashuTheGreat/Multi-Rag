from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
import logging
from langchain_core.messages import HumanMessage

from api.middlewares.authentication_middleware import authenticate_user
from api.schemas.chat_schema import ChatRequest
from src.graphs.builder import graph

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(authenticate_user)])

@router.post("/chat")
async def chat_endpoint(
    request: Request,
    chat_request: ChatRequest
):
    try:
        thread_id = request.state.thread_id
        
        logger.info("Chat request for thread %s: %s", thread_id, chat_request.message)
        
        initial_state = {
            "messages": [HumanMessage(content=chat_request.message)]
        }
        
        result = await graph.ainvoke(
            initial_state, 
            config={"configurable": {"thread_id": thread_id}}
        )
        
        return JSONResponse(
            content={
                "success": True,
                "response": result.get("ai_response", "No response generated")
            },
            status_code=200
        )
    except Exception as e:
        logger.error("Chat failed: %s", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)
