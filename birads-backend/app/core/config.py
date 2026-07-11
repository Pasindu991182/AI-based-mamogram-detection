"""Application settings loaded from environment variables.

Uses pydantic-settings so every value can be overridden via the environment
or a local .env file. See .env.example for the full list.
"""
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# birads-backend/  (two parents up from app/core/config.py)
BASE_DIR = Path(__file__).resolve().parents[2]


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
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    GOOGLE_CLIENT_ID: str = ""  # OAuth client id (web)

    # Comma-separated list of allowed frontend origins for CORS.
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # --- Database ---
    # SQLite for dev; switch to postgresql+psycopg://... for production.
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'birads.db'}"

    # --- Storage ---
    # "local" or "cloudinary"
    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_DIR: Path = BASE_DIR / "uploads"
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    CLOUDINARY_FOLDER: str = "birads"

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
