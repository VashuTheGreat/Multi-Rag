from fastapi import Request, HTTPException
from src.core.logger import logger


async def authenticate_user(request: Request, user_id: str | None = None, thread_id: str | None = None):
    with logger.span("🔐 Authenticating user and thread session"):
        try:
            user_id = user_id or request.query_params.get("user_id") or request.headers.get("user_id") or request.headers.get("x-user-id")
            thread_id = thread_id or request.query_params.get("thread_id") or request.headers.get("thread_id") or request.headers.get("x-thread-id")

            if not user_id or not thread_id:
                logger.warning("⚠️ Authentication rejected: missing user_id or thread_id", user_id=user_id, thread_id=thread_id)
                raise HTTPException(
                    status_code=401,
                    detail={"success": False, "message": "user_id and thread_id are required", "data": None},
                )
            request.state.user_id = user_id
            request.state.thread_id = thread_id
            logger.info("✅ Authentication successful", user_id=user_id, thread_id=thread_id)
        except HTTPException:
            raise
        except Exception as e:
            logger.error("❌ Authentication error encountered", error=str(e))
            raise HTTPException(
                status_code=401,
                detail={"success": False, "message": "Authentication failed", "data": None},
            )


async def authenticate_only_thread(request: Request, thread_id: str | None = None):
    with logger.span("🔐 Authenticating thread"):
        try:
            thread_id = (
                thread_id
                or request.query_params.get("thread_id")
                or request.headers.get("thread_id")
                or request.headers.get("x-thread-id")
            )

            if not thread_id and request.headers.get("content-type", "").startswith("application/json"):
                try:
                    body = await request.json()
                    if isinstance(body, dict):
                        thread_id = body.get("thread_id") or (
                            body.get("metadata", {}).get("thread_id")
                            if isinstance(body.get("metadata"), dict)
                            else None
                        )
                except Exception:
                    pass

            if not thread_id:
                logger.warning("⚠️ Authentication rejected: missing thread_id", thread_id=thread_id)
                raise HTTPException(
                    status_code=401,
                    detail={"success": False, "message": "thread_id is required", "data": None},
                )
            request.state.thread_id = thread_id
            logger.info("✅ Thread authenticated successfully", thread_id=thread_id)
        except HTTPException:
            raise
        except Exception as e:
            logger.error("❌ Authentication error encountered", error=str(e))
            raise HTTPException(
                status_code=401,
                detail={"success": False, "message": "Authentication failed", "data": None},
            )
