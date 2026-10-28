from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.core.logger import logger

router = APIRouter(tags=["Web"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))



# ==================== The Frontend UI ===============================
@router.get("/", response_class=HTMLResponse, summary="Serve Multi-RAG Chat Interface")
async def get_index(request: Request):
    logger.info("Rendering Multi-RAG Web Interface")
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": "Multi-RAG",
            "tagline": "Chai & Code Advanced Retrieval Pipeline",
        },
    )
