from fastapi import File, UploadFile,File
from pydantic import BaseModel


class UploadState(BaseModel):
    uploaded_file:UploadFile=File(...)
