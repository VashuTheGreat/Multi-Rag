from dotenv import load_dotenv
load_dotenv()   # ← must be FIRST so os.getenv works in all imported modules

import uvicorn as uv
from api.main import app
from logger import *
from fastapi.staticfiles import StaticFiles
from src.MultiRag.constants import DATA_FOLDER_PATH, DB_FOLDER_PATH
import os
app.mount("/static", StaticFiles(directory="static"), name="static")
os.makedirs("images", exist_ok=True)
app.mount("/blog/images", StaticFiles(directory="images"), name="blog_images")
# app.mount("/images", StaticFiles(directory="images"), name="blog_images")

os.makedirs(DATA_FOLDER_PATH, exist_ok=True)
os.makedirs(DB_FOLDER_PATH, exist_ok=True)

if __name__ == "__main__":
    uv.run(
        "main:app",
        host="0.0.0.0",
        port=7860,
        reload=False,
        reload_excludes=["db/*", "data/*", "logs/*", "vector_db/*", ".venv/*"],
    )