import os
import shutil
from typing import List
from fastapi import Request, UploadFile, File, HTTPException
from src.core.logger import logger
from src.constants import INGESTION_FOLDER_NAME, PUBLIC_DIRECTOR_NAME


PUBLIC_TEMP_DIR = os.path.join(PUBLIC_DIRECTOR_NAME, INGESTION_FOLDER_NAME)
os.makedirs(PUBLIC_TEMP_DIR, exist_ok=True)


async def multer_middleware(
    request: Request,
    file: UploadFile = File(default=None),
):
    saved_paths: List[str] = []
    with logger.span("📂 Upload middleware processing"):
        try:
            if not file:
                logger.debug("⚠️ No file uploaded in request")
                yield []
                return

            thread_id = getattr(request.state, "thread_id", "default")
            dest_dir = os.path.join(PUBLIC_TEMP_DIR, str(thread_id))
            os.makedirs(dest_dir, exist_ok=True)
            file_path = os.path.join(dest_dir, file.filename)

            logger.info("💾 Storing uploaded file", file_name=file.filename, destination=file_path)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            saved_paths.append(file_path)
            logger.info("✅ Uploaded file stored successfully", file_path=file_path)

            yield saved_paths

        except HTTPException:
            raise
        except Exception as e:
            logger.error("❌ Failed to store uploaded file", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

        finally:
            for file_path in saved_paths:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info("🧹 Cleaned up temporary upload file", file_path=file_path)
                except Exception as clean_err:
                    logger.error("❌ Failed to clean up temporary file", file_path=file_path, error=str(clean_err))

            if saved_paths:
                dest_dir = os.path.dirname(saved_paths[0])
                if os.path.exists(dest_dir) and not os.listdir(dest_dir):
                    os.rmdir(dest_dir)
                    logger.debug("🧹 Cleaned up empty upload directory", directory=dest_dir)
