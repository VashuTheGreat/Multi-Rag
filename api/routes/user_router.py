import logging

from fastapi import APIRouter,BackgroundTasks
from fastapi import Request
import uuid
from fastapi.responses import JSONResponse
from api.constants import DEFAULT_COOKIE_MAX_AGE_SECONDS,PUBLIC_FOLDER_FILE_PATH
import os
import shutil
from src.graphs.builder import deleteThread as GraphThreadDeletor
from src.constants import ARTIFACT_DIR
router = APIRouter()

import asyncio

async def delete_thread(thread_id: str, delay_seconds: int):
    """Utility function to delete a thread after a specific delay."""
    if delay_seconds > 0:
        logging.info(f"Waiting {delay_seconds} seconds before deleting thread: {thread_id}")
        await asyncio.sleep(delay_seconds)

    logging.info(f"Starting deletion of thread data for thread_id: {thread_id}")
    
    try:
        path1 = os.path.join(ARTIFACT_DIR, thread_id)
        path2 = os.path.join(PUBLIC_FOLDER_FILE_PATH, thread_id)
        
        if os.path.exists(path1):
            shutil.rmtree(path1)
            logging.info(f"Deleted artifact data for path: {path1}")
        if os.path.exists(path2):
            shutil.rmtree(path2)
            logging.info(f"Deleted public folder data for path: {path2}")
        try:    
            GraphThreadDeletor(thread_id)
        except Exception as e:
            logging.error(f"Error during graph thread deletion for thread_id {thread_id}: {e}")    
        logging.info(f"Completed deletion of thread data for thread_id: {thread_id}")
    except Exception as e:
        logging.error(f"Error deleting thread data for thread_id {thread_id}: {e}")


@router.get("/login/{seconds}", tags=["User"])
async def login(request: Request, seconds: int, background_tasks: BackgroundTasks):
    """Endpoint to handle user login. Sets a cookie and schedules data deletion."""
    
    thread_id = str(uuid.uuid4())
    
    response = JSONResponse(content={"message": "Login successful.","thread_id": thread_id}, status_code=200)
    response.set_cookie(
        key="thread_id", 
        value=thread_id, 
        httponly=True,
        max_age=DEFAULT_COOKIE_MAX_AGE_SECONDS
    )
    
    background_tasks.add_task(delete_thread, thread_id=thread_id, delay_seconds=seconds)

    return response
