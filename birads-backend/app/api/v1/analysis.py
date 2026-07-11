"""Tier 1-3 endpoint: upload CC/MLO, run the full imaging pipeline."""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.analysis import Analysis
from app.models.case import Case
from app.models.user import User
from app.schemas.analysis import AnalysisResponse
from app.services import pipeline
from app.storage import get_storage
from app.utils.imaging import base64_to_png_bytes

logger = get_logger(__name__)
router = APIRouter(prefix="/analyze", tags=["analysis"])


@router.post("", response_model=AnalysisResponse)
async def analyze(
    patient_age: float = Form(...),
    case_id: int | None = Form(None),
    file_cc: UploadFile | None = File(None),
    file_mlo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cc_bytes = await file_cc.read() if file_cc and file_cc.filename else None
    mlo_bytes = await file_mlo.read() if file_mlo and file_mlo.filename else None
    if not cc_bytes and not mlo_bytes:
        raise HTTPException(400, "Upload at least one image (CC or MLO view).")

    try:
        result = pipeline.run(cc_bytes, mlo_bytes, patient_age)
    except ValueError as exc:
        raise HTTPException(400, str(exc))

    # Persist if attached to a case owned by the user.
    if case_id is not None:
        case = db.get(Case, case_id)
        if case and case.owner_id == current_user.id:
            _store_images(case, cc_bytes, mlo_bytes)
            _persist_analysis(db, case, result)
            result.case_id = case_id

    return result


def _store_images(
    case: Case,
    cc_bytes: bytes | None,
    mlo_bytes: bytes | None,
) -> None:
    """Upload the original CC/MLO images to storage; save URLs on the case.

    Failures are logged but never break the analysis response.
    """
    storage = get_storage()

    def _try_upload(data: bytes, name: str) -> str | None:
        try:
            return storage.save_bytes(data, name)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Image upload failed for %s: %s", name, exc)
            return None

    if cc_bytes:
        url = _try_upload(cc_bytes, f"cases/{case.id}/cc.png")
        if url:
            case.cc_image_url = url
    if mlo_bytes:
        url = _try_upload(mlo_bytes, f"cases/{case.id}/mlo.png")
        if url:
            case.mlo_image_url = url
    # Overlay + mask URLs are stored in _persist_analysis (needs the analysis row).


def _persist_analysis(db: Session, case: Case, result: AnalysisResponse) -> None:
    wc = result.worst_case_radiomics
    analysis = case.analysis or Analysis(case_id=case.id)
    if wc:
        analysis.circularity = wc.circularity
        analysis.margin_integrity = wc.margin_integrity
        analysis.orientation_index = wc.orientation_index
        analysis.max_diameter = wc.max_diameter
        analysis.contrast_ratio = wc.contrast_ratio
        analysis.density_score = wc.density_score
    analysis.birads_code = result.overall_birads_code
    analysis.birads_label = result.overall_birads_label
    analysis.raw_payload = result.model_dump_json()

    # Upload overlay + mask (first view that has them) to storage.
    storage = get_storage()
    for view in result.analyzed_views:
        try:
            if view.overlay_image_base64 and not analysis.overlay_url:
                analysis.overlay_url = storage.save_bytes(
                    base64_to_png_bytes(view.overlay_image_base64),
                    f"cases/{case.id}/overlay.png",
                )
            if view.mask_image_base64 and not analysis.mask_url:
                analysis.mask_url = storage.save_bytes(
                    base64_to_png_bytes(view.mask_image_base64),
                    f"cases/{case.id}/mask.png",
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Mask/overlay upload failed: %s", exc)

    case.status = "analyzed"
    db.add(analysis)
    db.commit()
