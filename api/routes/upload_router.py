from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import JSONResponse
import uuid
import os
import logging
from api.constants import PUBLIC_FOLDER_FILE_PATH

router = APIRouter()

@router.post("", tags=["File"])
async def upload_file(request: Request, file: UploadFile = File(...)):
    try:
        user = request.scope.get("user")
        if not user:
            return JSONResponse(content={"error": "pls login"}, status_code=401)

        thread_id = user.thread_id
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_location = os.path.join(PUBLIC_FOLDER_FILE_PATH, thread_id, unique_filename)

        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logging.info(f"File '{file.filename}' uploaded successfully for thread '{thread_id}'.")
        
        return JSONResponse(
            content={
                "message": "File uploaded successfully",
                "filename": unique_filename,
                "thread_id": thread_id
            }, 
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error occurred while saving the file: {e}")
        return JSONResponse(content={"error": "Failed to upload the file."}, status_code=500)
    finally:
        await file.close()
