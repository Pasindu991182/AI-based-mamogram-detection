"""FastAPI application entrypoint."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.db.session import init_db
from app.services.model_registry import warmup

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting %s (%s)", settings.PROJECT_NAME, settings.ENVIRONMENT)
    init_db()           # dev convenience; use Alembic in production
    warmup()            # no-op when LAZY_MODEL_LOAD is True
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve locally stored uploads when using the local storage backend.
if settings.STORAGE_BACKEND == "local":
    Path(settings.LOCAL_STORAGE_DIR).mkdir(parents=True, exist_ok=True)
    app.mount(
        "/uploads",
        StaticFiles(directory=str(settings.LOCAL_STORAGE_DIR)),
        name="uploads",
    )

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["health"])
def root():
    return {
        "name": settings.PROJECT_NAME,
        "status": "running",
        "docs": "/docs",
        "api": settings.API_V1_PREFIX,
    }


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
