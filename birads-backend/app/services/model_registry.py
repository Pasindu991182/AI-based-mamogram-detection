"""Lazy, single-instance loader for all ML artefacts.

Heavy models (the 241 MB Keras U-Net, VGG16) are loaded on first use so the
API can boot instantly during development. Each loader caches its result.
"""
from functools import lru_cache

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@lru_cache
def get_seg_model():
    """ResNet50-UNet segmentation model (Keras)."""
    from tensorflow.keras.models import load_model

    logger.info("Loading segmentation model: %s", settings.seg_model_path.name)
    return load_model(str(settings.seg_model_path), compile=False)


@lru_cache
def get_vgg_extractor():
    """VGG16 global-average-pooled feature extractor."""
    from tensorflow.keras.applications.vgg16 import VGG16

    logger.info("Loading VGG16 feature extractor")
    return VGG16(weights="imagenet", include_top=False, pooling="avg")


@lru_cache
def get_birads_model():
    import joblib

    return joblib.load(str(settings.birads_model_path))


@lru_cache
def get_birads_scaler():
    import joblib

    return joblib.load(str(settings.birads_scaler_path))


@lru_cache
def get_acr_model():
    import joblib

    return joblib.load(str(settings.acr_model_path))


@lru_cache
def get_acr_scaler():
    import joblib

    return joblib.load(str(settings.acr_scaler_path))


@lru_cache
def get_er_artifacts():
    """Tier 5 ensemble + scaler. Returns (model, scaler) or (None, None)."""
    import joblib

    if not settings.er_model_path.exists():
        logger.warning("ER model not found at %s — using stub.", settings.er_model_path)
        return None, None
    model = joblib.load(str(settings.er_model_path))
    scaler = (
        joblib.load(str(settings.er_scaler_path))
        if settings.er_scaler_path.exists()
        else None
    )
    return model, scaler


def warmup() -> None:
    """Optionally pre-load models at startup (when LAZY_MODEL_LOAD is False)."""
    if settings.LAZY_MODEL_LOAD:
        return
    get_seg_model()
    get_vgg_extractor()
    get_birads_model()
    get_birads_scaler()
    get_acr_model()
    get_acr_scaler()
