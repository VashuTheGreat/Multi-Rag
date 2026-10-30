import os
import aiosqlite
from typing import Optional
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from src.core.logger import logger
from src.app_config import get_app_config

_checkpointer: Optional[AsyncSqliteSaver] = None
_connection: Optional[aiosqlite.Connection] = None


async def init_checkpointer(db_path: Optional[str] = None) -> AsyncSqliteSaver:
    """Initialize AsyncSqliteSaver with aiosqlite connection."""
    global _checkpointer, _connection
    if _checkpointer is not None and _connection is not None:
        return _checkpointer

    if not db_path:
        config = get_app_config()
        db_path = getattr(config, "checkpoint_db_path", "db/checkpoints.db")

    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    logger.info("Initializing AsyncSqliteSaver database connection", db_path=db_path)
    _connection = await aiosqlite.connect(db_path)
    _checkpointer = AsyncSqliteSaver(_connection)
    await _checkpointer.setup()
    logger.info("AsyncSqliteSaver checkpointer setup complete", db_path=db_path)
    return _checkpointer


async def close_checkpointer() -> None:
    """Close the underlying aiosqlite connection."""
    global _checkpointer, _connection
    if _connection is not None:
        logger.info("Closing AsyncSqliteSaver database connection")
        try:
            await _connection.close()
        except Exception as e:
            logger.error("Error while closing database connection", error=str(e))
        finally:
            _connection = None
            _checkpointer = None


def get_checkpointer() -> Optional[AsyncSqliteSaver]:
    """Retrieve the active checkpointer instance."""
    global _checkpointer
    return _checkpointer


async def get_async_checkpointer(db_path: Optional[str] = None) -> AsyncSqliteSaver:
    """Async getter that ensures checkpointer is initialized before returning."""
    global _checkpointer
    if _checkpointer is None:
        await init_checkpointer(db_path)
    return _checkpointer


get_memory = get_checkpointer
