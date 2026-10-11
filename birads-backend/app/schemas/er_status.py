from typing import Optional

from pydantic import BaseModel, Field


class ERPredictRequest(BaseModel):
    case_id: Optional[int] = None
    age: int = Field(..., ge=0, le=120)
    # Auto-filled from Tier 2 max_diameter when omitted by the client.
    tumor_size: float = Field(..., ge=0)
    histologic_grade: int = Field(..., ge=1, le=3)
    cellularity: str  # Low | Moderate | High
    menopausal_state: str  # Pre | Post
    histologic_subtype: str  # Ductal | Lobular | Mixed | Other
    lymph_nodes_positive: int = Field(..., ge=0)


class FeatureContribution(BaseModel):
    feature: str          # "Histologic grade"
    value: str            # "3"
    direction: str        # "ER+" | "ER-" | "neutral"
    magnitude: float = 0  # 0..1 relative strength of the push


class ERPredictResponse(BaseModel):
    case_id: Optional[int] = None
    er_result: str  # "ER Positive" | "ER Negative"
    confidence: str  # High | Medium | Low
    probability_positive: float  # 0..1
    probability_negative: float  # 0..1
    model_version: str = "stub"
    recommendation: str
    treatment_signal: str = ""               # short clinical signal for the UI banner
    contributions: list[FeatureContribution] = []
