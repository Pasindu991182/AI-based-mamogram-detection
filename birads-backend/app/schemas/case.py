from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.analysis import RadiomicFeatures
from app.schemas.report import FeatureRow


class CaseCreate(BaseModel):
    patient_ref: str = ""
    patient_age: Optional[int] = None


class CaseUpdate(BaseModel):
    """Partial update of editable case fields."""
    patient_ref: Optional[str] = None
    patient_age: Optional[int] = None


class CaseOut(BaseModel):
    id: int
    patient_ref: str
    patient_age: Optional[int] = None
    cc_image_url: Optional[str] = None
    mlo_image_url: Optional[str] = None
    status: str
    created_at: datetime

    # Worklist summary fields (flattened from related tiers).
    views: Optional[str] = None              # "CC+MLO"
    birads_code: Optional[int] = None
    birads_label: Optional[str] = None
    er_result: Optional[str] = None
    er_probability_positive: Optional[float] = None
    report_finalized: bool = False

    class Config:
        from_attributes = True

    @classmethod
    def from_case(cls, case) -> "CaseOut":
        """Flatten a Case ORM object (+ its related tiers) for the worklist."""
        analysis = getattr(case, "analysis", None)
        er = getattr(case, "er_prediction", None)
        report = getattr(case, "report", None)

        views = None
        if case.cc_image_url and case.mlo_image_url:
            views = "CC+MLO"
        elif case.cc_image_url:
            views = "CC"
        elif case.mlo_image_url:
            views = "MLO"

        return cls(
            id=case.id,
            patient_ref=case.patient_ref,
            patient_age=case.patient_age,
            cc_image_url=case.cc_image_url,
            mlo_image_url=case.mlo_image_url,
            status=case.status,
            created_at=case.created_at,
            views=views,
            birads_code=getattr(analysis, "birads_code", None),
            birads_label=getattr(analysis, "birads_label", None),
            er_result=getattr(er, "er_result", None),
            er_probability_positive=getattr(er, "probability_positive", None),
            report_finalized=bool(getattr(report, "finalized_at", None)),
        )


# --- Full case detail (View page: images, features, report, ER) ---------
class AnalysisDetail(BaseModel):
    mask_url: Optional[str] = None
    overlay_url: Optional[str] = None
    features: Optional[RadiomicFeatures] = None
    feature_rows: list[FeatureRow] = []
    birads_code: Optional[int] = None
    birads_label: Optional[str] = None
    predicted_acr: Optional[int] = None


class ReportDetail(BaseModel):
    id: Optional[int] = None
    generated_text: str = ""
    edited_text: Optional[str] = None
    generator: str = "template"
    finalized_at: Optional[datetime] = None


class ERDetail(BaseModel):
    age: Optional[int] = None
    tumor_size: Optional[float] = None
    histologic_grade: Optional[int] = None
    cellularity: Optional[str] = None
    menopausal_state: Optional[str] = None
    histologic_subtype: Optional[str] = None
    lymph_nodes_positive: Optional[int] = None
    er_result: Optional[str] = None
    confidence: Optional[str] = None
    probability_positive: Optional[float] = None
    model_version: str = "stub"


class CaseDetail(BaseModel):
    id: int
    patient_ref: str
    patient_age: Optional[int] = None
    cc_image_url: Optional[str] = None
    mlo_image_url: Optional[str] = None
    status: str
    created_at: datetime

    analysis: Optional[AnalysisDetail] = None
    report: Optional[ReportDetail] = None
    er_prediction: Optional[ERDetail] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_case(cls, case) -> "CaseDetail":
        """Build the full read-only view (images, features, report, ER)."""
        from app.services.tier4_report import feature_rows

        analysis = getattr(case, "analysis", None)
        report = getattr(case, "report", None)
        er = getattr(case, "er_prediction", None)

        analysis_detail = None
        if analysis is not None:
            features = None
            rows: list[FeatureRow] = []
            if analysis.circularity is not None:
                features = RadiomicFeatures(
                    circularity=analysis.circularity,
                    margin_integrity=analysis.margin_integrity,
                    orientation_index=analysis.orientation_index,
                    max_diameter=analysis.max_diameter,
                    contrast_ratio=analysis.contrast_ratio,
                    density_score=analysis.density_score,
                )
                rows = feature_rows(features)
            analysis_detail = AnalysisDetail(
                mask_url=analysis.mask_url,
                overlay_url=analysis.overlay_url,
                features=features,
                feature_rows=rows,
                birads_code=analysis.birads_code,
                birads_label=analysis.birads_label,
                predicted_acr=analysis.predicted_acr,
            )

        report_detail = (
            ReportDetail(
                id=report.id,
                generated_text=report.generated_text,
                edited_text=report.edited_text,
                generator=report.generator,
                finalized_at=report.finalized_at,
            )
            if report is not None
            else None
        )

        er_detail = (
            ERDetail(
                age=er.age,
                tumor_size=er.tumor_size,
                histologic_grade=er.histologic_grade,
                cellularity=er.cellularity,
                menopausal_state=er.menopausal_state,
                histologic_subtype=er.histologic_subtype,
                lymph_nodes_positive=er.lymph_nodes_positive,
                er_result=er.er_result,
                confidence=er.confidence,
                probability_positive=er.probability_positive,
                model_version=er.model_version,
            )
            if er is not None
            else None
        )

        return cls(
            id=case.id,
            patient_ref=case.patient_ref,
            patient_age=case.patient_age,
            cc_image_url=case.cc_image_url,
            mlo_image_url=case.mlo_image_url,
            status=case.status,
            created_at=case.created_at,
            analysis=analysis_detail,
            report=report_detail,
            er_prediction=er_detail,
        )
