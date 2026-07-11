from typing import Optional

from pydantic import BaseModel


class RadiomicFeatures(BaseModel):
    circularity: float
    margin_integrity: float
    orientation_index: float
    max_diameter: float
    contrast_ratio: float
    density_score: float


class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int


class BiRadsRule(BaseModel):
    """One human-readable rule that fired during BI-RADS classification."""

    feature: str            # "Circularity"
    condition: str          # "0.41 < 0.50"
    interpretation: str     # "shape is Irregular"
    severity: str = "info"  # info | warn | high


class FeatureImportance(BaseModel):
    feature: str
    weight: float           # 0..1, sums to ~1 across the list


class BiRadsExplanation(BaseModel):
    headline: str = ""                          # "Why BI-RADS 4?"
    model: str = "white-box classifier · ACR BI-RADS Atlas"
    rules: list["BiRadsRule"] = []
    feature_importance: list["FeatureImportance"] = []


class ViewAnalysis(BaseModel):
    view: str  # "CC View" | "MLO View"
    predicted_class: str  # "Mass Detected" | "No Mass Detected"
    bounding_box: Optional[BoundingBox] = None
    radiomic_features: Optional[RadiomicFeatures] = None
    overlay_image_base64: Optional[str] = None
    mask_image_base64: Optional[str] = None
    predicted_acr: Optional[int] = None
    birads_code: Optional[int] = None
    birads_label: Optional[str] = None


class AnalysisResponse(BaseModel):
    status: str = "success"
    case_id: Optional[int] = None
    patient_age: Optional[int] = None
    worst_case_radiomics: Optional[RadiomicFeatures] = None
    overall_birads_code: Optional[int] = None
    overall_birads_label: Optional[str] = None
    explanation: Optional[BiRadsExplanation] = None
    analyzed_views: list[ViewAnalysis] = []
