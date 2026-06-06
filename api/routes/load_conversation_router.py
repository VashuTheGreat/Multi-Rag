from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import logging
import os

from src.graphs.builder import load_conversation as GraphConversationLoader
router = APIRouter()



@router.get("", tags=['Conversation'])
async def load_conversation(request: Request):
    try:
        thread_id = request.scope['user'].thread_id
        messages = await GraphConversationLoader(thread_id)
        return JSONResponse(content={"messages": messages},status_code=200)
        
    except Exception as e:
        logging.error(f"Error loading conversation: {e}")
        return JSONResponse(content={"error": "Failed to load conversation."}, status_code=500)