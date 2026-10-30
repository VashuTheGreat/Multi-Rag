from typing import Any, Dict, List
from langchain_core.messages import messages_to_dict
from src.core.logger import logger
from src.service.memory.async_sql import get_checkpointer, get_async_checkpointer


async def load_conversation(thread_id: str) -> List[Dict[str, Any]]:
    """Retrieve and serialize conversation messages for a given thread_id."""
    with logger.span("load_conversation", thread_id=thread_id):
        try:
            cp = get_checkpointer()
            if cp is None:
                cp = await get_async_checkpointer()

            config: Dict[str, Any] = {"configurable": {"thread_id": thread_id}}

            state = await cp.aget_tuple(config=config)
            if state is None or not state.checkpoint:
                logger.info("Thread {thread_id} not found or has no checkpoints.", thread_id=thread_id)
                return []

            channel_values = state.checkpoint.get("channel_values", {})
            raw_messages = channel_values.get("messages", [])
            serialized_messages = messages_to_dict(raw_messages) if raw_messages else []
            logger.info("Loaded {count} messages for thread {thread_id}", count=len(serialized_messages), thread_id=thread_id)
            return serialized_messages
        except Exception as e:
            logger.error("Error loading conversation for thread {thread_id}: {err}", thread_id=thread_id, err=str(e))
            return []


async def delete_user_conversation(thread_id: str) -> bool:
    """Delete a thread from the checkpointer storage."""
    with logger.span("delete_user_conversation", thread_id=thread_id):
        try:
            cp = get_checkpointer()
            if cp is None:
                cp = await get_async_checkpointer()

            config: Dict[str, Any] = {"configurable": {"thread_id": thread_id}}

            state = await cp.aget_tuple(config=config)
            if state is None:
                logger.info("Thread {thread_id} not found, nothing to delete.", thread_id=thread_id)
                return False

            await cp.adelete_thread(thread_id=thread_id)
            logger.info("Thread {thread_id} deleted successfully from checkpointer.", thread_id=thread_id)
            return True
        except Exception as e:
            logger.error("delete_user_conversation failed for thread {thread_id}: {err}", thread_id=thread_id, err=str(e))
            return False


async def get_all_threads() -> List[Dict[str, Any]]:
    """Retrieve all unique conversation threads stored in the checkpointer."""
    with logger.span("get_all_threads"):
        try:
            cp = get_checkpointer()
            if cp is None:
                cp = await get_async_checkpointer()

            threads_map: Dict[str, Dict[str, Any]] = {}

            # Iterate over checkpoints in checkpointer
            async for checkpoint_tuple in cp.alist(None):
                cfg = checkpoint_tuple.config.get("configurable", {})
                tid = cfg.get("thread_id")
                if not tid:
                    continue

                checkpoint = checkpoint_tuple.checkpoint or {}
                ts = checkpoint.get("ts")
                channel_values = checkpoint.get("channel_values", {})
                messages = channel_values.get("messages", [])

                # Derive a title from the first human message if available
                title = "New Conversation"
                for msg in messages:
                    content = ""
                    if isinstance(msg, dict):
                        if msg.get("type") in {"human", "user"}:
                            content = msg.get("content", "")
                    elif hasattr(msg, "type") and getattr(msg, "type") in {"human", "user"}:
                        content = getattr(msg, "content", "")

                    if content:
                        title = content[:40] + ("..." if len(content) > 40 else "")
                        break

                if tid not in threads_map:
                    threads_map[tid] = {
                        "thread_id": tid,
                        "title": title,
                        "created_at": ts,
                        "updated_at": ts,
                        "message_count": len(messages),
                    }
                else:
                    # Update message count or timestamp if later
                    existing = threads_map[tid]
                    if len(messages) > existing["message_count"]:
                        existing["message_count"] = len(messages)
                        if title != "New Conversation":
                            existing["title"] = title
                    if ts and (not existing["updated_at"] or ts > existing["updated_at"]):
                        existing["updated_at"] = ts

            threads_list = list(threads_map.values())
            logger.info("Retrieved {count} active threads", count=len(threads_list))
            return threads_list
        except Exception as e:
            logger.error("Error retrieving all threads: {err}", err=str(e))
            return []
