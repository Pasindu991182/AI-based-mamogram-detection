"""Pydantic schemas for Case-Based Reasoning (CBR) and similar case retrieval."""
from typing import Any, Optional
from pydantic import BaseModel

from app.schemas.analysis import RadiomicFeatures


class CbrSimilarCase(BaseModel):
    case_id: str
    patient_age: int
    similarity_percentage: float  # e.g. 91.5
    ground_truth_birads: int       # 2, 3, 4, 5
    ground_truth_label: str       # "BI-RADS 2 (Benign)", etc.
    biopsy_outcome: str           # e.g. "Fibroadenoma (Benign)"
    is_malignant: bool
    er_status: str                # "ER+" | "ER-" | "N/A (Benign)"
    clinical_action_taken: str    # e.g. "Routine screening at 12 months"
    key_morphology: str           # "Circumscribed margins, oval shape"
    thumbnail_svg: str            # Clean SVG visualization of lesion
    features: dict[str, float]


class CbrAnalysisResult(BaseModel):
    matches: list[CbrSimilarCase] = []
    biopsy_concordance: str       # e.g. "3 of 3 (100%) historical cases confirmed Benign on biopsy"
    malignant_count: int
    benign_count: int
    actionable_recommendation: str  # ACR guideline recommendation
    clinical_rationale: str


class CbrQueryRequest(BaseModel):
    features: RadiomicFeatures
    birads_code: Optional[int] = None
    patient_age: Optional[int] = 54
    top_k: int = 3
