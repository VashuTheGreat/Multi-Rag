from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from api.states.user_state import User

class AuthenticateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path=request.url.path
        if path.startswith('/api/v1/user/login'):
            return await call_next(request)
        thread_id = request.cookies.get("thread_id")
        if not thread_id:
            return JSONResponse({"error": "pls login"}, status_code=401)
        
        request.scope["user"] = User(thread_id=thread_id)
        return await call_next(request)
