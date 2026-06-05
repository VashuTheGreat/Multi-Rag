from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates



template = Jinja2Templates(directory="api/templates")
router=APIRouter()


@router.get("/",tags=['frontend'])
async def Home_route(request:Request):
    return template.TemplateResponse("home.html", {"request": request})

