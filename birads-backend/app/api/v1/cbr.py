"""Case-Based Reasoning (CBR) API Router."""
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.cbr import CbrAnalysisResult, CbrQueryRequest, CbrSimilarCase
from app.services import cbr_engine

router = APIRouter(prefix="/cbr", tags=["cbr"])


@router.post("/similar-cases", response_model=CbrAnalysisResult)
def retrieve_similar_cases(
    body: CbrQueryRequest,
    current_user: User = Depends(get_current_user),
):
    """Retrieve top-K verified historical patient cases and clinical concordance."""
    return cbr_engine.find_similar_cases(
        features=body.features,
        birads_code=body.birads_code,
        patient_age=body.patient_age,
        top_k=body.top_k,
    )


@router.get("/reference-library", response_model=list[dict])
def get_reference_library(
    current_user: User = Depends(get_current_user),
):
    """Browse all reference cases currently indexed in the CBR memory bank."""
    return cbr_engine.load_reference_cases()
