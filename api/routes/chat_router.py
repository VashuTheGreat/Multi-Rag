import json
from typing import Any, AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse, JSONResponse
from langchain_core.messages import HumanMessage, AIMessage
from api.middlewares.authentication_middleware import authenticate_only_thread
from api.schemas.chat_schema import ChatRequest
from src.core.logger import logger
from src.agents.graph import get_graph

router = APIRouter(dependencies=[Depends(authenticate_only_thread)],tags=["Chat"])

graph = get_graph()


async def stream_chat(message: str, thread_id: str, metadata: dict = {}) -> AsyncGenerator[str, None]:
    try:
        logger.info("🌊 stream_chat started: thread_id={thread_id}", thread_id=thread_id)
        active_graph = graph
        if active_graph is None:
            active_graph = get_graph()

        if active_graph is None:
            logger.error("❌ Graph runner is not configured")
            err_payload = json.dumps({"type": "error", "message": "Graph engine not configured"})
            yield f"data:{err_payload}\n\n"
            return

        initial_state = {
            "user_message": message,
            "messages": [],
            "retreived_content":None,
            "queries":None

        }
        config = {"configurable": {"thread_id": thread_id}}

        async for event in active_graph.astream_events(initial_state, config=config, version="v2"):
            event_type = event.get("event")

            match event_type:
                # 1. Tool execution start (e.g. solver tool requested or retriever)
                case "on_tool_start":
                    tool_name = event.get("name")
                    tool_input = event.get("data", {}).get("input")
                    payload = json.dumps({"type": "tool_start", "tool": tool_name, "input": tool_input})
                    yield f"data:{payload}\n\n"

                case "on_chain_start" if event.get("name") in {"retriever", "retriever_node"}:
                    tool_input = event.get("data", {}).get("input")
                    payload = json.dumps({"type": "tool_start", "tool": "retriever", "input": tool_input})
                    yield f"data:{payload}\n\n"

                # 2. Tool execution end (tool completed)
                case "on_tool_end":
                    tool_name = event.get("name")
                    tool_output = str(event.get("data", {}).get("output"))
                    payload = json.dumps({"type": "tool_end", "tool": tool_name, "output": tool_output})
                    yield f"data:{payload}\n\n"

                case "on_chain_end" if event.get("name") in {"retriever", "retriever_node"}:
                    tool_output = str(event.get("data", {}).get("output"))
                    payload = json.dumps({"type": "tool_end", "tool": "retriever", "output": tool_output})
                    yield f"data:{payload}\n\n"

                case "on_custom_event" if event.get("name") == "agent_stream":
                    data = event.get("data", {})
                    if isinstance(data, dict) and data.get("type"):
                        payload = json.dumps(data)
                        yield f"data:{payload}\n\n"

                # 3. Model token stream (only stream tokens from response nodes to the user UI)
                case "on_chat_model_stream":
                    langgraph_node = event.get("metadata", {}).get("langgraph_node")
                    # Ignore internal background node LLM streams (e.g. orchestrator_node, summary_node, query_generation_node, planner)
                    if langgraph_node and langgraph_node not in {"chat_node", "agent_node", "responder", "responder_node"}:
                        continue

                    chunk = event.get("data", {}).get("chunk")
                    if chunk:
                        msg = getattr(chunk, "message", chunk)
                        additional_kwargs = getattr(msg, "additional_kwargs", {}) or getattr(chunk, "additional_kwargs", {})
                        reasoning = (
                            additional_kwargs.get("reasoning_content")
                            or additional_kwargs.get("reasoning")
                            or additional_kwargs.get("thinking")
                        )
                        if reasoning:
                            payload = json.dumps({"type": "reasoning", "content": reasoning})
                            yield f"data:{payload}\n\n"
                        else:
                            content = getattr(chunk, "content", None) or getattr(msg, "content", None)
                            if content:
                                payload = json.dumps({"type": "token", "content": content})
                                yield f"data:{payload}\n\n"

                # 4. Final chain completed
                case "on_chain_end" if event.get("name") in {"chat_node", "agent_node", "responder", "responder_node"}:
                    output = event.get("data", {}).get("output", {})
                    ai_response = None
                    if isinstance(output, dict):
                        ai_response = output.get("ai_response")
                        if not ai_response:
                            msgs = output.get("messages", [])
                            if isinstance(msgs, list):
                                for m in reversed(msgs):
                                    if isinstance(m, AIMessage) or getattr(m, "type", "") == "ai":
                                        ai_response = m.content
                                        break
                    if ai_response:
                        payload = json.dumps({"type": "final", "ai_response": ai_response, "state": "completed"})
                        yield f"data:{payload}\n\n"

                case _:
                    pass

        logger.info("✅ stream_chat completed: thread_id={thread_id}", thread_id=thread_id)
    except Exception as e:
        logger.error("❌ stream_chat error: {error}", error=str(e))
        err_payload = json.dumps({"type": "error", "message": str(e)})
        yield f"data:{err_payload}\n\n"


# Alias for backward compatibility if imported elsewhere
stream_graph = stream_chat


@router.post(
    "/chat",
    summary="Chat with the RAG Pipeline (SSE Stream)",
    responses={
        200: {"description": "Server-Sent Events stream of AI response tokens."},
        400: {"description": "Pipeline execution error."},
        401: {"description": "Missing or invalid thread_id."},
        500: {"description": "Graph runner configuration error."},
    },
)
async def run_workflow(request: Request, payload: ChatRequest):
    """
    Send a message to the LangGraph RAG pipeline and receive a
    **Server-Sent Events (SSE)** stream of AI response tokens.

    ### Response
    `Content-Type: text/event-stream` — consume as SSE.
    """
    thread_id = getattr(request.state, "thread_id", None)
    with logger.span("💬 Processing chat request", thread_id=thread_id):
        try:
            logger.info("💬 chat endpoint invoked: thread_id={thread_id}", thread_id=thread_id)

            active_graph = graph
            if active_graph is None:
                try:
                    active_graph = get_graph()
                except Exception:
                    active_graph = None

            if active_graph is None:
                logger.error("❌ Graph runner is not configured")
                return JSONResponse(
                    content={"error": "Graph engine not configured"},
                    status_code=500,
                )

            config = {"configurable": {"thread_id": thread_id}} if thread_id else None

            if getattr(payload, "stream", True) is False:
                logger.info("⏳ Processing non-streaming chat request: thread_id={thread_id}", thread_id=thread_id)
                initial_state = {
                    "user_message": payload.message,
                }
                result = await active_graph.ainvoke(initial_state, config=config)

                ai_response = "No response generated"
                messages = result.get("messages", []) if isinstance(result, dict) else []
                for msg in reversed(messages):
                    if isinstance(msg, AIMessage) or getattr(msg, "type", "") == "ai":
                        ai_response = msg.content
                        break
                if ai_response == "No response generated" and isinstance(result, dict) and "ai_response" in result:
                    ai_response = result["ai_response"]

                logger.info("✅ Chat response generated successfully: thread_id={thread_id}", thread_id=thread_id)
                return JSONResponse(
                    content={
                        "success": True,
                        "response": ai_response,
                    },
                    status_code=200,
                )

            logger.info("🌊 Streaming chat response started: thread_id={thread_id}", thread_id=thread_id)
            return StreamingResponse(
                stream_chat(
                    message=payload.message,
                    thread_id=thread_id,
                    metadata=getattr(payload, "metadata", {}),
                ),
                media_type="text/event-stream",
                headers={
                    "Content-Type": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )
        except Exception as e:
            logger.error("❌ chat endpoint failed: {error}", error=str(e))
            return JSONResponse(content={"error": str(e)}, status_code=500)
