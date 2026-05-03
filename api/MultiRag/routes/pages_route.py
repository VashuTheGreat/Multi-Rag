import os
import fastapi
from fastapi import Request
from fastapi.templating import Jinja2Templates

router = fastapi.APIRouter()
templates = Jinja2Templates(directory="templates")

_APP_USER_ID = os.getenv("APP_API_KEY", "")

# @router.get("/")
# async def read_root(request: Request):
#     return templates.TemplateResponse(
#         request=request,
#         name="home.html",
#         context={"app_user_id": _APP_USER_ID}
#     )


@router.get("/")
async def chat_model(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={"app_user_id": _APP_USER_ID}
    )

# @router.get("/web")
# async def web_page(request: Request):
#     return templates.TemplateResponse(
#         request=request,
#         name="web.html",
#         context={"app_user_id": _APP_USER_ID}
#     )
