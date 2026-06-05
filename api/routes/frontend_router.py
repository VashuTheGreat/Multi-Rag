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
]

# All backend API URLs consumed by upload.html JavaScript.
# Keep them here so a single Python edit propagates everywhere.
UPLOAD_PAGE_URLS = {
    "login_base": "/api/v1/user/login",   # JS appends /{seconds}
    "upload":     "/api/v1/upload",
    "ingest":     "/api/v1/ingest",
    "chat_page":  "/chat",               # frontend route added later
}


# ─────────────────────────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────────────────────────

@router.get("/", tags=["frontend"])
async def home_route(request: Request):
    return template.TemplateResponse("home.html", {"request": request})


@router.get("/upload", tags=["frontend"])
async def upload_route(request: Request):
    return template.TemplateResponse(
        "upload.html",
        {
            "request":     request,
            "time_options": TIME_OPTIONS,
            "urls":        UPLOAD_PAGE_URLS,
        },
    )
