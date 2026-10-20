from fastapi import FastAPI
import logging

from api.routes.chat_router import router as chat_router
from api.routes.user_router import router as user_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Multi-RAG API")

app.include_router(chat_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
