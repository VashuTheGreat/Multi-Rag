from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

template = Jinja2Templates(directory="api/templates")
router = APIRouter()

# ─────────────────────────────────────────────────────────────────
#  JINJA CONTEXT CONSTANTS
#  Change values here — templates pick them up automatically.
# ─────────────────────────────────────────────────────────────────

# Session time-duration options shown on the upload page.
# Each dict must have: label, description, icon, seconds (int).
TIME_OPTIONS = [
    {
        "label": "1 Minute",
        "description": "Quick demo or sanity check",
        "icon": "⚡",
        "seconds": 60,
    },
    {
        "label": "2 Minutes",
        "description": "Standard exploration session",
        "icon": "🧪",
        "seconds": 120,
    },
    {
        "label": "3 Minutes",
        "description": "Deep-dive knowledge session",
        "icon": "🔬",
        "seconds": 180,
    },
     {
        "label": "10 Minutes",
        "description": "Very Deep-dive knowledge session",
        "icon": "🔬",
        "seconds": 300,
    }
]

# All backend API URLs consumed by upload.html JavaScript.
UPLOAD_PAGE_URLS = {
    "login_base": "/api/v1/user/login",
    "upload":     "/api/v1/upload",
    "ingest":     "/api/v1/ingest",
    "chat_page":  "/chat",
}

# API URLs for chat.html
CHAT_PAGE_URLS = {
    "chat":              "/api/v1/chat",
    "load_conversation": "/api/v1/conversation",
    "ingest":            "/api/v1/ingest",
    "upload_page":       "/upload",
}


# ─────────────────────────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────────────────────────

@router.get("/", tags=["frontend"])
async def home_route(request: Request):
    return template.TemplateResponse(
        request=request,
        name="home.html"
    )


@router.get("/upload", tags=["frontend"])
async def upload_route(request: Request):
    return template.TemplateResponse(
        request=request,
        name="upload.html",
        context={
            "time_options": TIME_OPTIONS,
            "urls":         UPLOAD_PAGE_URLS,
        },
    )


@router.get("/chat", tags=["frontend"])
async def chat_route(request: Request):
    return template.TemplateResponse(
        request=request,
        name="chat.html",
        context={
            "urls":    CHAT_PAGE_URLS,
        },
    )
