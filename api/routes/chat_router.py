import json
from typing import Any, AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse, JSONResponse
from langchain_core.messages import HumanMessage, AIMessage
from api.middlewares.authentication_middleware import authenticate_only_thread
from api.schemas.chat_schema import ChatRequest
from src.core.logger import logger
from src.agents.graph import get_graph
from src.service.memory.async_sql import get_checkpointer
from src.service.llm_provider.groq import AVAILABLE_MODELS, DEFAULT_MODEL



# ============== used emoji for frontend view =============================
router = APIRouter(dependencies=[Depends(authenticate_only_thread)],tags=["Chat"])

# metadata is additonal info for collection appart from user_message from end user
async def stream_chat(message: str, thread_id: str, metadata: dict = {}) -> AsyncGenerator[str, None]:
    try:
        logger.info("stream_chat started: thread_id={thread_id}", thread_id=thread_id)
        active_graph = get_graph(get_checkpointer())

        if active_graph is None:
            logger.error("Graph runner is not configured")
            err_payload = json.dumps({"type": "error", "message": "Graph engine not configured"})
            yield f"data:{err_payload}\n\n"
            return

        initial_state = {
            "user_message": message,
            "messages": [],
            "retreived_content":None,
            "queries":None

        }
        model = (metadata or {}).get("model", DEFAULT_MODEL)
        if model not in AVAILABLE_MODELS:
            yield f"data:{json.dumps({'type': 'error', 'message': 'Unsupported model selection'})}\n\n"
            return
        config = {"configurable": {"thread_id": thread_id, "model": model}}

        async for event in active_graph.astream_events(initial_state, config=config, version="v2"):
            event_type = event.get("event")
            event_name = event.get("name")
            lg_node = event.get("metadata", {}).get("langgraph_node") or event_name

            match event_type:
                # Node flow lifecycle events
                case "on_chain_start" if lg_node in {"guardrail", "guardrail_node"}:
                    payload = json.dumps({
                        "type": "node_flow",
                        "node": "guardrail",
                        "status": "running",
                        "title": "🛡️ Guardrails Invoked",
                        "description": "Checking input safety, injection patterns & topic scope..."
                    })
                    yield f"data:{payload}\n\n"

                case "on_chain_end" if lg_node in {"guardrail", "guardrail_node"}:
                    out = event.get("data", {}).get("output", {})
                    is_blocked = bool(out.get("is_blocked")) if isinstance(out, dict) else False
                    if is_blocked:
                        payload = json.dumps({
                            "type": "node_flow",
                            "node": "guardrail",
                            "status": "blocked",
                            "title": "🛑 Guardrail Blocked",
                            "description": "Query blocked by security or domain policy."
                        })
                    else:
                        payload = json.dumps({
                            "type": "node_flow",
                            "node": "guardrail",
                            "status": "completed",
                            "title": "🛡️ Guardrail Passed",
                            "description": "Input verified & approved for processing."
                        })
                    yield f"data:{payload}\n\n"

                case "on_chain_start" if lg_node in {"planner", "planner_node"}:
                    payload = json.dumps({
                        "type": "node_flow",
                        "node": "planner",
                        "status": "running",
                        "title": "📋 Planner Invoked",
                        "description": "Analyzing intent & determining execution path..."
                    })
                    yield f"data:{payload}\n\n"

                case "on_chain_end" if lg_node in {"planner", "planner_node"}:
                    out = event.get("data", {}).get("output", {})
                    route_to = out.get("route_to", "responder") if isinstance(out, dict) else "responder"
                    desc = "Routed to Knowledge Base Retriever" if route_to == "retriever" else "Direct LLM Responder selected"
                    payload = json.dumps({
                        "type": "node_flow",
                        "node": "planner",
                        "status": "completed",
                        "title": "📋 Planner Decided",
                        "description": desc
                    })
                    yield f"data:{payload}\n\n"

                case "on_chain_start" if lg_node in {"retriever", "retriever_node"}:
                    tool_input = event.get("data", {}).get("input")
                    payload = json.dumps({"type": "tool_start", "tool": "retriever", "input": tool_input})
                    yield f"data:{payload}\n\n"
                    flow_payload = json.dumps({
                        "type": "node_flow",
                        "node": "retriever",
                        "status": "running",
                        "title": "🔍 Retriever Invoked",
                        "description": "Searching hybrid vector & keyword knowledge base..."
                    })
                    yield f"data:{flow_payload}\n\n"

                case "on_chain_end" if lg_node in {"retriever", "retriever_node"}:
                    tool_output = str(event.get("data", {}).get("output"))
                    payload = json.dumps({"type": "tool_end", "tool": "retriever", "output": tool_output})
                    yield f"data:{payload}\n\n"
                    flow_payload = json.dumps({
                        "type": "node_flow",
                        "node": "retriever",
                        "status": "completed",
                        "title": "🔍 Retrieval Completed",
                        "description": "Relevant documents fetched and reranked."
                    })
                    yield f"data:{flow_payload}\n\n"

                case "on_chain_start" if lg_node in {"responder", "responder_node"}:
                    payload = json.dumps({
                        "type": "node_flow",
                        "node": "responder",
                        "status": "running",
                        "title": "✍️ Responder Invoked",
                        "description": "Generating answer..."
                    })
                    yield f"data:{payload}\n\n"

                case "on_chain_start" if lg_node in {"blocked_responder", "blocked_responder_node"}:
                    payload = json.dumps({
                        "type": "node_flow",
                        "node": "blocked_responder",
                        "status": "running",
                        "title": "🛑 Policy Handler Invoked",
                        "description": "Preparing policy refusal explanation..."
                    })
                    yield f"data:{payload}\n\n"

                case "on_chain_end" if lg_node in {"blocked_responder", "blocked_responder_node"}:
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
                    if not ai_response:
                        ai_response = "I cannot fulfill this request as it is outside the supported DevOps domain or violates safety policies."
                    token_payload = json.dumps({"type": "token", "content": ai_response})
                    yield f"data:{token_payload}\n\n"
                    final_payload = json.dumps({"type": "final", "ai_response": ai_response, "state": "completed"})
                    yield f"data:{final_payload}\n\n"
                    flow_payload = json.dumps({
                        "type": "node_flow",
                        "node": "blocked_responder",
                        "status": "completed",
                        "title": "🛑 Refusal Sent",
                        "description": "Policy refusal response delivered."
                    })
                    yield f"data:{flow_payload}\n\n"

                # Tool execution start along with name
                case "on_tool_start":
                    tool_name = event.get("name")
                    tool_input = event.get("data", {}).get("input")
                    payload = json.dumps({"type": "tool_start", "tool": tool_name, "input": tool_input})
                    yield f"data:{payload}\n\n"

                # Tool execution end
                case "on_tool_end":
                    tool_name = event.get("name")
                    tool_output = str(event.get("data", {}).get("output"))
                    payload = json.dumps({"type": "tool_end", "tool": tool_name, "output": tool_output})
                    yield f"data:{payload}\n\n"

                # for custom event yielding using dispatch etc
                case "on_custom_event" if event.get("name") == "agent_stream":
                    data = event.get("data", {})
                    if isinstance(data, dict) and data.get("type"):
                        payload = json.dumps(data)
                        yield f"data:{payload}\n\n"

                # model token stream (only stream tokens from response_node to the user UI)
                case "on_chat_model_stream":
                    langgraph_node = event.get("metadata", {}).get("langgraph_node")
                    # Ignore internal background node LLM streams (e.g. guardrail, planner)
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

                # Final chain completed final output in one shot
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
                    flow_payload = json.dumps({
                        "type": "node_flow",
                        "node": "responder",
                        "status": "completed",
                        "title": "✍️ Responder Finished",
                        "description": "Answer generated successfully."
                    })
                    yield f"data:{flow_payload}\n\n"


                case _:
                    pass

        logger.info("stream_chat completed: thread_id={thread_id}", thread_id=thread_id)
    except Exception as e:
        logger.error("stream_chat error: {error}", error=str(e))
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

    handles both cases Stream = True / False acc to payload enduser
    """
    thread_id = getattr(request.state, "thread_id", None)
    with logger.span("Processing chat request", thread_id=thread_id):
        try:
            logger.info("chat endpoint invoked: thread_id={thread_id}", thread_id=thread_id)

            metadata = payload.metadata or {}
            model = metadata.get("model", DEFAULT_MODEL)
            if model not in AVAILABLE_MODELS:
                return JSONResponse(
                    content={"error": "Unsupported model selection"},
                    status_code=422,
                )

            active_graph = get_graph(get_checkpointer())

            if active_graph is None:
                logger.error("Graph runner is not configured")
                return JSONResponse(
                    content={"error": "Graph engine not configured"},
                    status_code=500,
                )

            config = {"configurable": {"thread_id": thread_id, "model": model}} if thread_id else {"configurable": {"model": model}}

            # if stream is False direct answer
            if getattr(payload, "stream", True) is False:
                logger.info("Processing non-streaming chat request: thread_id={thread_id}", thread_id=thread_id)
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

                logger.info("Chat response generated successfully: thread_id={thread_id}", thread_id=thread_id)
                return JSONResponse(
                    content={
                        "success": True,
                        "response": ai_response,
                    },
                    status_code=200,
                )

            # stream is True yield SSE Responses
            logger.info("Streaming chat response started: thread_id={thread_id}", thread_id=thread_id)
            return StreamingResponse(
                stream_chat(
                    message=payload.message,
                    thread_id=thread_id,
                    metadata=metadata,
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
            logger.error("chat endpoint failed: {error}", error=str(e))
            return JSONResponse(content={"error": str(e)}, status_code=500)
