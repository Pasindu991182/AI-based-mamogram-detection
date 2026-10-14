"""Application settings loaded from environment variables.

Uses pydantic-settings so every value can be overridden via the environment
or a local .env file. See .env.example for the full list.
"""
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# birads-backend/  (two parents up from app/core/config.py)
BASE_DIR = Path(__file__).resolve().parents[2]

DEFAULT_JWT_SECRET = "change-me-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    PROJECT_NAME: str = "Explainable BI-RADS Diagnostic Engine"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # --- Security / Auth ---
    JWT_SECRET: str = DEFAULT_JWT_SECRET
    JWT_ALGORITHM: str = "HS256"
    # Short-lived access token, held in browser memory only. The session
    # itself lives in a server-side, revocable refresh token (httpOnly cookie).
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_HOURS: int = 12  # one working shift
    REFRESH_COOKIE_NAME: str = "birads_refresh"

    # Password policy + brute-force lockout
    PASSWORD_MIN_LENGTH: int = 12
    MAX_FAILED_LOGINS: int = 5
    LOCKOUT_MINUTES: int = 15

    # Comma-separated list of allowed frontend origins for CORS.
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # --- Database ---
    # PostgreSQL is the supported database (see docker-compose.yml):
    #   postgresql+psycopg://birads:<password>@localhost:5432/birads
    # The SQLite default only exists so tests and a first boot work unconfigured.
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'birads.db'}"

    # --- Storage ---
    # Patient images are stored AES-256-GCM encrypted in the database and served
    # only through signed, expiring URLs (see app/core/media_token.py).
    # "database" (default) | "local" (plain files, debugging only)
    STORAGE_BACKEND: str = "database"
    # 32 random bytes, base64url. Generate with:
    #   python -c "import base64,os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"
    # Losing this key makes every stored image unreadable — back it up separately.
    DATA_ENCRYPTION_KEY: str = ""
    LOCAL_STORAGE_DIR: Path = BASE_DIR / "uploads"
    MEDIA_URL_TTL_SECONDS: int = 900  # 15 minutes

    # --- ML weights ---
    ML_WEIGHTS_DIR: Path = BASE_DIR / "ml_weights"
    SEG_MODEL_FILE: str = "resnet50_unet_inbreast_final.keras"
    BIRADS_MODEL_FILE: str = "xgboost_model.pkl"
    BIRADS_SCALER_FILE: str = "scaler.pkl"
    ACR_MODEL_FILE: str = "acr_xgb_model.pkl"
    ACR_SCALER_FILE: str = "acr_scaler.pkl"
    # Tier 5 (optional — stub used until present)
    ER_MODEL_FILE: str = "er_ensemble.pkl"
    ER_SCALER_FILE: str = "er_scaler.pkl"

    # Load heavy CV/ML models lazily on first request instead of at startup.
    LAZY_MODEL_LOAD: bool = True

    # --- Tier 6: Clinical RAG assistant ---
    OPENAI_API_KEY: str = ""
    RAG_INDEX_DIR: Path = BASE_DIR / "rag_index"      # persisted FAISS index
    RAG_DOCS_DIR: Path = BASE_DIR / "rag_docs"        # optional local PDFs/txt
    RAG_LLM_MODEL: str = "gpt-4o-mini"
    RAG_EMBED_MODEL: str = "text-embedding-3-small"
    RAG_TOP_K: int = 4
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200

    @model_validator(mode="after")
    def _refuse_unsafe_production_config(self) -> "Settings":
        if self.is_production and (
            self.JWT_SECRET == DEFAULT_JWT_SECRET or len(self.JWT_SECRET) < 32
        ):
            raise ValueError(
                "JWT_SECRET must be a random value of at least 32 characters "
                "when ENVIRONMENT=production."
            )
        if self.is_production and self.STORAGE_BACKEND != "database":
            raise ValueError("STORAGE_BACKEND must be 'database' in production.")
        if self.is_production and not self.DATA_ENCRYPTION_KEY:
            raise ValueError("DATA_ENCRYPTION_KEY must be set when ENVIRONMENT=production.")
        return self

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]

    # Resolved absolute paths to weight files
    @property
    def seg_model_path(self) -> Path:
        return self.ML_WEIGHTS_DIR / self.SEG_MODEL_FILE

    @property
    def birads_model_path(self) -> Path:
        return self.ML_WEIGHTS_DIR / self.BIRADS_MODEL_FILE

    @property
    def birads_scaler_path(self) -> Path:
        return self.ML_WEIGHTS_DIR / self.BIRADS_SCALER_FILE

    @property
    def acr_model_path(self) -> Path:
        return self.ML_WEIGHTS_DIR / self.ACR_MODEL_FILE

    @property
    def acr_scaler_path(self) -> Path:
        return self.ML_WEIGHTS_DIR / self.ACR_SCALER_FILE

    @property
    def er_model_path(self) -> Path:
        return self.ML_WEIGHTS_DIR / self.ER_MODEL_FILE

    @property
    def er_scaler_path(self) -> Path:
        return self.ML_WEIGHTS_DIR / self.ER_SCALER_FILE

    # RAG readiness helpers
    @property
    def rag_key_configured(self) -> bool:
        return bool(self.OPENAI_API_KEY)

    @property
    def rag_index_ready(self) -> bool:
        return (self.RAG_INDEX_DIR / "index.faiss").exists()

    @property
    def rag_ready(self) -> bool:
        return self.rag_key_configured and self.rag_index_ready


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
