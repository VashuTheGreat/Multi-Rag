from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.middlewares.Authenticate_middleware import AuthenticateMiddleware

from api.routes.upload_router import router as upload_router
from api.routes.user_router import router as user_router
from api.routes.ingest_docs_router import router as ingest_router
from api.routes.chat_router import router as chat_router

app = FastAPI( 
    description="This is a MultiRag App",
    title="Multi-Rag App",
    version="0.0.1",
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthenticateMiddleware)



@app.get("/")
async def hello():
    return {"Hello": True}


app.include_router(upload_router,prefix="/api")
app.include_router(user_router,prefix="/api")
app.include_router(ingest_router,prefix="/api")
app.include_router(chat_router,prefix="/api")
