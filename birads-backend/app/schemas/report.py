from typing import Optional

from pydantic import BaseModel

from app.schemas.analysis import RadiomicFeatures


class ReportPatientMeta(BaseModel):
    patient_ref: str = ""
    age: Optional[int] = None
    sex: str = "F"
    laterality: str = ""            # e.g. "Left breast"
    menopausal_state: str = ""      # e.g. "Post-menopausal"
    referring_facility: str = ""
    study_date: str = ""            # ISO date; server fills today if blank


class ReportERInfo(BaseModel):
    er_result: str                  # "ER Positive" | "ER Negative"
    probability_positive: float     # 0..1
    confidence: str                 # High | Medium | Low
    inputs_summary: str = ""        # human-readable list of the 7 inputs


class ReportGenerateRequest(BaseModel):
    case_id: Optional[int] = None
    features: RadiomicFeatures
    birads_code: int
    patient_age: Optional[int] = None
    predicted_class: str = "Mass Detected"
    patient: Optional[ReportPatientMeta] = None
    er: Optional[ReportERInfo] = None


# --- Structured document (matches the professional report layout) ---
class MetaItem(BaseModel):
    label: str
    value: str


class FeatureRow(BaseModel):
    feature: str
    value: str
    interpretation: str


class BiRadsSection(BaseModel):
    category: str          # "BI-RADS 4 (suspicious abnormality)"
    rationale: str
    recommendation: str


class ReportDocument(BaseModel):
    title: str = "Mammography Radiology Report"
    subtitle: str = (
        "AI-Assisted Breast Cancer Decision Support System — Auto-generated report"
    )
    meta: list[MetaItem] = []
    segmentation: str = ""
    features: list[FeatureRow] = []
    birads: BiRadsSection
    er: Optional[ReportERInfo] = None
    impression: str = ""


class ReportUpdateRequest(BaseModel):
    edited_text: str
    finalize: bool = False


class ReportResponse(BaseModel):
    id: Optional[int] = None
    case_id: Optional[int] = None
    generator: str = "template"
    impression: str = ""            # the NLP narrative (editable)
    generated_text: str = ""        # full plain-text rendering (DB + print fallback)
    edited_text: Optional[str] = None
    document: Optional[ReportDocument] = None

    class Config:
        from_attributes = True
