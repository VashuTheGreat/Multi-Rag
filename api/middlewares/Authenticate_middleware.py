from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from api.states.user_state import User


class AuthenticateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # ── Non-API paths (frontend pages, static assets, favicon) ──────────
        # Never block these — anyone can browse the UI freely.
        if not path.startswith("/api/v1/"):
            return await call_next(request)

        # ── Public API endpoints (no cookie needed) ──────────────────────────
        if path.startswith("/api/v1/user/login"):
            return await call_next(request)

        # ── Protected API endpoints — cookie required ────────────────────────
        thread_id = request.cookies.get("thread_id")
        if not thread_id:
            return JSONResponse({"error": "pls login"}, status_code=401)

        request.scope["user"] = User(thread_id=thread_id)
        return await call_next(request)
