from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from langchain_core.messages import HumanMessage

from api.middlewares.authentication_middleware import authenticate_user
from api.schemas.chat_schema import ChatRequest
from src.core.logger import logger

try:
    from src.graphs.builder import graph
except ImportError:
    try:
        from app_backup.graphs.builder import graph
    except ImportError:
        graph = None

router = APIRouter(dependencies=[Depends(authenticate_user)])


@router.post("/chat")
async def chat_endpoint(
    request: Request,
    chat_request: ChatRequest,
):
    thread_id = request.state.thread_id
    with logger.span("💬 Processing chat request", thread_id=thread_id):
        try:
            logger.info("💬 Received chat message", thread_id=thread_id, message=chat_request.message)

            if graph is None:
                logger.error("❌ Graph runner is not configured")
                return JSONResponse(
                    content={"error": "Graph engine not configured"},
                    status_code=500,
                )

            initial_state = {
                "messages": [HumanMessage(content=chat_request.message)],
            }

            result = await graph.ainvoke(
                initial_state,
                config={"configurable": {"thread_id": thread_id}},
            )

            logger.info("✅ Chat response generated successfully", thread_id=thread_id)
            return JSONResponse(
                content={
                    "success": True,
                    "response": result.get("ai_response", "No response generated"),
                },
                status_code=200,
            )
        except Exception as e:
            logger.error("❌ Chat processing failed", thread_id=thread_id, error=str(e))
            return JSONResponse(content={"error": str(e)}, status_code=500)
