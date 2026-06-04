from fastapi import APIRouter
from fastapi import Request
import uuid
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/login", tags=["User"])
async def login(request: Request):
    """Endpoint to handle user login. Sets a cookie with a unique thread_id for the user."""
    
    thread_id = str(uuid.uuid4())
    response = JSONResponse(content={"message": "Login successful."}, status_code=200)
    response.set_cookie(key="thread_id", value=thread_id, httponly=True)

    return response
