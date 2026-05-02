from accelerate import logging
import fastapi
from fastapi import UploadFile, Request, BackgroundTasks
import os
import shutil
import asyncio
import logging
from src.MultiRag.graph.builder import deleteThread
from utils.asyncHandler import asyncHandler
from src.MultiRag.nodes.retreiver_check_node import clear_cached_retriever

from api.constants import CONTENT_PERSISTENT_TIME,DATA_FOLDER_PATH,DB_FOLDER_PATH
router = fastapi.APIRouter()


@asyncHandler
async def delete_folder_after_time(user_id):

    await asyncio.sleep(CONTENT_PERSISTENT_TIME)

    folder_path = f"{DATA_FOLDER_PATH}/{user_id}"
    db_path = f"{DB_FOLDER_PATH}/{user_id}"

    # Step 1: null refs, gc.collect(), clear_system_cache() — in that order
    clear_cached_retriever(db_path)
    await deleteThread(user_id)

    # Step 2: give Windows 3s to fully release OS-level file locks after GC
    await asyncio.sleep(3)

    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        logging.info(f"Folder deleted: {folder_path}")

    if os.path.exists(db_path):
        for attempt in range(6):
            try:
                shutil.rmtree(db_path)
                logging.info(f"DB deleted: {db_path}")
                return
            except PermissionError as e:
                logging.warning(f"DB delete attempt {attempt+1} failed: {e}")
                await asyncio.sleep(3)

        logging.error(f"Failed to delete DB after all retries: {db_path}")



    


@router.post("/post_content")
async def post_content(
    req: Request,
    file: UploadFile,
    background_tasks: BackgroundTasks
):
    try:
        user_id = req.headers.get("user_id")

        folder = f"{DATA_FOLDER_PATH}/{user_id}"
        os.makedirs(folder, exist_ok=True)

        file_path = f"{folder}/{file.filename}"

        with open(file_path, "wb") as f:
            f.write(await file.read())

        # start background delete timer
        # background_tasks.add_task(delete_folder_after_time, user_id)

        logging.info(f"File uploaded succesfully file_path:{file_path}")
        return {"message": "File uploaded successfully"}

    except Exception as e:
        return {"message": "File upload failed"}