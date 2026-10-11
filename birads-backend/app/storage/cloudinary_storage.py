"""Cloudinary storage for production. Survives ephemeral-disk redeploys."""
from app.core.config import settings
from app.storage.base import StorageBackend


class CloudinaryStorage(StorageBackend):
    def __init__(self) -> None:
        import cloudinary  # imported lazily

        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )
        self._cloudinary = cloudinary

    def save_bytes(self, data: bytes, filename: str, content_type: str = "image/png") -> str:
        import cloudinary.uploader

        public_id = f"{settings.CLOUDINARY_FOLDER}/{filename.rsplit('.', 1)[0]}"
        result = cloudinary.uploader.upload(
            data,
            public_id=public_id,
            resource_type="image",
            overwrite=True,
        )
        return result["secure_url"]
