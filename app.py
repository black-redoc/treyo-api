import os
from dotenv import load_dotenv

if os.getenv("ENVIRONMENT") == "development":
    load_dotenv()

from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, Response, Request
from contextlib import asynccontextmanager

from src.tasks.router import router as task_router
from src.tasks import models as tasks_model
from src.projects.router import router as project_router
from src.projects import models as projects_model
from src.users.router import router as users_router
from src.users import models as users_model
from src.settings.database import create_database


from src.settings.database import SessionLocal, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()
    yield


app = FastAPI(lifespan=lifespan)

tasks_model.Base.metadata.create_all(bind=engine)
projects_model.Base.metadata.create_all(bind=engine)
users_model.Base.metadata.create_all(bind=engine)


@app.get("/healthcheck")
def health():
    return "OK"


@app.get("/", status_code=200)
def health():
    return None


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(task_router)
app.include_router(project_router)
app.include_router(users_router)
