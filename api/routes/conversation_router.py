from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from src.core.logger import logger
from api.helper.conversation_helper import (
    get_all_threads,
    load_conversation,
    delete_user_conversation,
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get(
    "",
    summary="Get all conversation threads",
    responses={
        200: {"description": "List of all active conversation threads"},
        500: {"description": "Internal server error"},
    },
)
async def list_threads():
    """Retrieve all saved conversation threads from checkpointer."""
    with logger.span("Endpoint list_threads"):
        try:
            threads = await get_all_threads()
            return JSONResponse(
                content={
                    "success": True,
                    "count": len(threads),
                    "threads": threads,
                },
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error("Failed to list threads: {err}", err=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list threads: {str(e)}",
            )


@router.get(
    "/{thread_id}",
    summary="Get messages for a specific conversation thread",
    responses={
        200: {"description": "Messages retrieved for thread"},
        404: {"description": "Thread not found or empty"},
        500: {"description": "Internal server error"},
    },
)
async def get_thread_conversation(thread_id: str):
    """Retrieve serialized message history for the given thread_id."""
    with logger.span("Endpoint get_thread_conversation", thread_id=thread_id):
        try:
            messages = await load_conversation(thread_id=thread_id)
            return JSONResponse(
                content={
                    "success": True,
                    "thread_id": thread_id,
                    "count": len(messages),
                    "messages": messages,
                },
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error("Failed to load conversation {thread_id}: {err}", thread_id=thread_id, err=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to load conversation: {str(e)}",
            )


@router.delete(
    "/{thread_id}",
    summary="Delete a conversation thread",
    responses={
        200: {"description": "Thread deleted successfully"},
        404: {"description": "Thread not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_thread(
    thread_id: str,
):
    """Delete a conversation thread from the checkpointer."""
    with logger.span("Endpoint delete_thread", thread_id=thread_id):
        try:
            deleted = await delete_user_conversation(thread_id=thread_id)
            if not deleted:
                logger.warning("Thread {thread_id} not found to delete", thread_id=thread_id)
                return JSONResponse(
                    content={
                        "success": False,
                        "message": f"Thread {thread_id} not found or already deleted",
                    },
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            return JSONResponse(
                content={
                    "success": True,
                    "message": f"Thread {thread_id} deleted successfully",
                },
                status_code=status.HTTP_200_OK,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to delete thread {thread_id}: {err}", thread_id=thread_id, err=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete thread: {str(e)}",
            )
