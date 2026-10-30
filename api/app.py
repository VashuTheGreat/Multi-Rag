from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from api.routes.ingestion_router import router as IngestionRouter
from api.routes.chat_router import router as ChatRouter
from api.routes.web_router import router as WebRouter
from api.routes.conversation_router import router as ConversationRouter
from src.core.logger import initialise_logger, logger
from src.service.memory.async_sql import init_checkpointer, close_checkpointer
from src.agents.graph import get_graph
from src.constants import DATA_BASE_FOLDER_NAME

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# load blocking havy task before the server starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    initialise_logger()
    logger.info("🚀 Multi-RAG API starting up")
    checkpointer = await init_checkpointer(db_path=DATA_BASE_FOLDER_NAME)
    get_graph(checkpointer)
    yield
    await close_checkpointer()
    logger.info("🛑 Multi-RAG API shutting down")


app = FastAPI(title="Multi-RAG API", lifespan=lifespan)
logger.instrument_fastapi(app)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(IngestionRouter, prefix="/api/v1")
app.include_router(ChatRouter, prefix="/api/v1")
app.include_router(ConversationRouter, prefix="/api/v1")
app.include_router(WebRouter)


