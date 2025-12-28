from fastapi import FastAPI
from routers.auth import router as auth_router
from db.database import engine, Base
from routers.task import router as tasks_router
from routers.workspace import router as workspace_router
import models
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",  # your React dev server
]

app = FastAPI(title="Smart Task Manager API")
app.include_router(auth_router)
Base.metadata.create_all(bind=engine)

app.include_router(tasks_router)
app.include_router(workspace_router)

@app.get("/")
def health_check():
    return {"status": "running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)