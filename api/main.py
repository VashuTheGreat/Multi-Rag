from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from api.MultiRag.routes import chat_route, uploader_route, pages_route
from api.Web.routes import web_talk_routes
from api.Blog.routes import page_route_blog,blog_router
from api.Web.routes import page_route_web
app = FastAPI()

# @app.middleware("http")
# async def check_user_id(request: Request, call_next):
#     # Skip middleware for static files and page routes to allow initial connection
#     public_routes = [
#         "/",
#         "/chat",
#         "/web",
#         "/blog",
#         "/docs",
#         "/redoc",
#         "/openapi.json",
#         "/favicon.ico",
#     ]
#     if request.url.path.startswith("/static") or request.url.path.startswith("/blog/images") or request.url.path in public_routes:
#         return await call_next(request)

#     user_id = request.headers.get("user_id") or request.query_params.get("user_id")

#     if not user_id:
#         return JSONResponse(
#             status_code=401,
#             content={"message": "user_id header missing"}
#         )

#     response = await call_next(request)
#     return response

# app.include_router(pages_route.router)
app.include_router(prefix="/api/v1/chat", router=chat_route.router)
app.include_router(prefix="/api/v1/uploader", router=uploader_route.router)





# # -------------------- Web -------------------------------
# app.include_router(page_route_web.router)
# app.include_router(prefix="/web",router=web_talk_routes.router)





# # ------------ Blog --------------------
# app.include_router(page_route_blog.router)
# app.include_router(prefix="/blog",router=blog_router.router)

