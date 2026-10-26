from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from src.ingestion.processor import process_file
from api.middlewares.multi_middleware import multer_middleware
from src.core.logger import logger

router = APIRouter(tags=["Ingestion"])


@router.post("/ingest", status_code=status.HTTP_200_OK)
async def ingest_data(
    file_paths: List[str] = Depends(multer_middleware),
):
    with logger.span("📥 Ingestion API endpoint: {file_count} file(s)", file_count=len(file_paths) if file_paths else 0):
        if not file_paths:
            logger.warning("⚠️ No files provided for ingestion endpoint")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files uploaded",
            )

        logger.info("📥 Processing files for ingestion", count=len(file_paths), files=file_paths)

        processed_results = []
        try:
            for path in file_paths:
                logger.info("📄 Ingesting file via pipeline", file_path=path)
                res = await process_file(file_path=path)
                if not res:
                    logger.error("❌ Failed to process file during ingestion", file=path)
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to process file: {path}",
                    )
                processed_results.append(res)

            logger.info("✅ All files ingested successfully", count=len(file_paths))

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
            logger.error("❌ Ingestion process failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
