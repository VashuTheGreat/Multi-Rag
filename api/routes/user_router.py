from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
import logging
from typing import List

from api.middlewares.authentication_middleware import authenticate_user
from api.middlewares.multi_middleware import multer_middleware
from src.graphs.builder import graph

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(authenticate_user)])

@router.post("/ingest")
async def ingest_data(
    request: Request, 
    file_paths: List[str] = Depends(multer_middleware)
):
    try:
        thread_id = request.state.thread_id
        
        if not file_paths:
            return JSONResponse(content={"error": "No files uploaded"}, status_code=400)
            
        logger.info("Ingesting files for thread %s: %s", thread_id, file_paths)
        
        initial_state = {
            "file_paths": file_paths,
        }
        
        result = await graph.ainvoke(
            initial_state, 
            config={"configurable": {"thread_id": thread_id}}
        )
        
        logger.info("Ingestion completed for thread %s", thread_id)
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Ingestion successful",
                "vector_store_path": result.get("vector_store_file_path")
            },
            status_code=200
        )
    except Exception as e:
        logger.error("Ingestion failed: %s", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)
