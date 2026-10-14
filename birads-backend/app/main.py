"""FastAPI application entrypoint."""
from contextlib import asynccontextmanager
from cryptography.exceptions import InvalidTag
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.media_token import verify_media_token
from app.db.session import init_db
from app.services.model_registry import warmup
from app.storage import get_storage

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting %s (%s)", settings.PROJECT_NAME, settings.ENVIRONMENT)
    if settings.DATABASE_URL.startswith("sqlite"):
        init_db()       # tests / unconfigured first boot only
    # PostgreSQL schemas are managed by Alembic: `alembic upgrade head`.
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

@app.get("/uploads/{rel_path:path}", tags=["media"], include_in_schema=False)
def serve_upload(rel_path: str, exp: int = 0, sig: str = ""):
    """Serve a stored patient image only against a valid, unexpired signature.

    Images are decrypted on the way out and never exposed through a public
    static mount. Links are minted per response (app/core/media_token.py) and
    expire, so a URL that leaks out of the browser stops working shortly after.
    """
    if not verify_media_token(rel_path, exp, sig):
        raise HTTPException(status_code=403, detail="Invalid or expired media link.")

    try:
        stored = get_storage().read_bytes(rel_path)
    except InvalidTag:
        logger.error("Stored image %s failed its integrity check", rel_path)
        stored = None
    if stored is None:
        raise HTTPException(status_code=404, detail="Not found.")

    data, content_type = stored
    return Response(
        content=data,
        media_type=content_type,
        headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"},
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
