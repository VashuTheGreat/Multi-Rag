from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.routes.chat_router import router as chat_router
from api.routes.user_router import router as user_router

@asynccontextmanager
async def lifespan(app:FastAPI):
    from app.core.logger import initialise_logger, logger
    initialise_logger()
    logger.info("Multi-RAG API starting up")
    yield
    logger.info("Multi-RAG API shutting down")


app = FastAPI(title="Multi-RAG API",lifespan=lifespan)

app.include_router(chat_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
