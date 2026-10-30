import os
from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from typing import List, Optional

from src.ingestion.processor import process_file
from api.middlewares.multi_middleware import multer_middleware
from src.core.logger import logger
from src.app_config import get_app_config

router = APIRouter(tags=["Ingestion"])


def verify_ingestion_password(
    x_ingestion_password: Optional[str] = Header(None, alias="x-ingestion-password"),
    x_password: Optional[str] = Header(None, alias="x-password"),
    password: Optional[str] = Query(None),
):
    """Autherity check only autherized people can ingest documents"""
    expected_password = getattr(get_app_config(), "ingestion_password", None) or os.getenv("INGESTION_PASSWORD", "aloo")
    provided = x_ingestion_password or x_password or password
    if not provided or provided != expected_password:
        logger.warning("Unauthorized ingestion attempt: invalid or missing password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing ingestion password",
        )
    return True


@router.post("/ingest", status_code=status.HTTP_200_OK)
async def ingest_data(
    file_paths: List[str] = Depends(multer_middleware),
    authenticated: bool = Depends(verify_ingestion_password),
):
    with logger.span("Ingestion API endpoint: {file_count} file(s)", file_count=len(file_paths) if file_paths else 0):
        if not file_paths:
            logger.warning("No files provided for ingestion endpoint")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files uploaded",
            )

        logger.info("Processing files for ingestion", count=len(file_paths), files=file_paths)

        processed_results = []
        try:
            for path in file_paths:
                logger.info("Ingesting file via pipeline", file_path=path)
                res = await process_file(file_path=path)
                if not res:
                    logger.error("Failed to process file during ingestion", file=path)
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to process file: {path}",
                    )
                processed_results.append(res)

            logger.info("All files ingested successfully", count=len(file_paths))

            return {
                "message": f"Successfully ingested {len(file_paths)} file(s)",
                "data": {
                    "files": file_paths,
                    "results": processed_results,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Ingestion process failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
