import os
from fastapi import FastAPI
from routers.auth import router as auth_router
from db.database import engine, Base
from routers.task import router as tasks_router
from routers.workspace import router as workspace_router
from routers.share import router as share_router
import models
from fastapi.middleware.cors import CORSMiddleware

# Get frontend URL from environment, with local dev fallback
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

origins = [
    "http://localhost:5173",  # local React dev server
    frontend_url,  # production Vercel URL
]

app = FastAPI(title="Smart Task Manager API")

# Add CORS middleware first (before routes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
Base.metadata.create_all(bind=engine)

app.include_router(tasks_router)
app.include_router(workspace_router)
app.include_router(share_router)

@app.get("/")
def health_check():
    return {"status": "running"}