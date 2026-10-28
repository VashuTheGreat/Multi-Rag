from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.routes.ingestion_router import router as IngestionRouter
from api.routes.chat_router import router as ChatRouter
from src.core.logger import initialise_logger, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialise_logger()
    logger.info("🚀 Multi-RAG API starting up")
    yield
    logger.info("🛑 Multi-RAG API shutting down")


app = FastAPI(title="Multi-RAG API", lifespan=lifespan)
logger.instrument_fastapi(app)

app.include_router(IngestionRouter, prefix="/api/v1")
app.include_router(ChatRouter, prefix="/api/v1")

