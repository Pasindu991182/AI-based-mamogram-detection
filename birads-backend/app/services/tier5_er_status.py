"""Tier 5 — ER status prediction from 7 basic clinical inputs.

If a trained ensemble (er_ensemble.pkl) is present it is used; otherwise a
transparent heuristic stub returns a structured, plausible result so the full
end-to-end flow works for the demo. Replace by dropping the .pkl into
ml_weights/ — no code change needed.
"""
import numpy as np

from app.schemas.er_status import (
    ERPredictRequest,
    ERPredictResponse,
    FeatureContribution,
)
from app.services.model_registry import get_er_artifacts

# Label encodings — MUST match the sklearn LabelEncoder fitted during training
# (METABRIC ER model v2). Order is alphabetical, exactly as LabelEncoder produced.
#   Cellularity   : High=0, Low=1, Moderate=2, (unknown/nan=3)
#   Menopausal    : Post=0, Pre=1, (unknown/nan=2)
#   Subtype       : Ductal/NST=0 ... Tubular/ cribriform=7, (unknown/nan=8)
CELLULARITY_MAP = {"High": 0, "Low": 1, "Moderate": 2}
MENOPAUSE_MAP = {"Post": 0, "Pre": 1}
SUBTYPE_MAP = {
    "Ductal/NST": 0,
    "Lobular": 1,
    "Medullary": 2,
    "Metaplastic": 3,
    "Mixed": 4,
    "Mucinous": 5,
    "Other": 6,
    "Tubular/ cribriform": 7,
}

# Fallback codes for values the model never saw (mirror the training 'nan' class).
CELLULARITY_UNKNOWN = 3
MENOPAUSE_UNKNOWN = 2
SUBTYPE_UNKNOWN = 6  # "Other"


def _confidence_band(prob: float) -> str:
    margin = abs(prob - 0.5)
    if margin >= 0.30:
        return "High"
    if margin >= 0.15:
        return "Medium"
    return "Low"


def _recommendation(er_positive: bool, confidence: str) -> str:
    if er_positive:
        return (
            "ER-positive prediction suggests potential responsiveness to hormone "
            "therapy. Confirm with IHC before initiating treatment."
        )
    return (
        "ER-negative prediction suggests hormone therapy may be ineffective; "
        "chemotherapy pathways should be considered. Confirm with IHC."
    )


def _treatment_signal(er_positive: bool) -> str:
    if er_positive:
        return "ER+ → likely hormone-therapy candidate. Plan early while awaiting IHC."
    return "ER− → consider chemotherapy pathways. Plan early while awaiting IHC."


def _contributions(req: ERPredictRequest) -> list[FeatureContribution]:
    """Transparent, signed drivers behind the prediction (UI explainability)."""
    out: list[FeatureContribution] = []

    grade_dir = {1: "ER+", 2: "neutral", 3: "ER-"}[req.histologic_grade]
    out.append(FeatureContribution(
        feature="Histologic grade", value=str(req.histologic_grade),
        direction=grade_dir, magnitude=0.0 if grade_dir == "neutral" else 0.34,
    ))
    out.append(FeatureContribution(
        feature="Menopausal state", value=req.menopausal_state,
        direction="ER+" if req.menopausal_state == "Post" else "ER-",
        magnitude=0.22,
    ))
    nodes_dir = "ER-" if req.lymph_nodes_positive > 0 else "neutral"
    out.append(FeatureContribution(
        feature="Lymph nodes +", value=str(req.lymph_nodes_positive),
        direction=nodes_dir,
        magnitude=min(0.06 * req.lymph_nodes_positive, 0.30),
    ))
    size_dir = "ER-" if req.tumor_size > 30 else "neutral"
    out.append(FeatureContribution(
        feature="Tumor size", value=f"{req.tumor_size:.1f} mm",
        direction=size_dir, magnitude=0.12 if size_dir == "ER-" else 0.0,
    ))
    return out


def _encode(req: ERPredictRequest) -> np.ndarray:
    """Build the 7-feature vector in the exact column order the model expects:
    [age, tumor_size, histologic_grade, cellularity, menopausal_state,
     histologic_subtype, lymph_nodes_positive]."""
    return np.array([[
        req.age,
        req.tumor_size,
        req.histologic_grade,
        CELLULARITY_MAP.get(req.cellularity, CELLULARITY_UNKNOWN),
        MENOPAUSE_MAP.get(req.menopausal_state, MENOPAUSE_UNKNOWN),
        SUBTYPE_MAP.get(req.histologic_subtype, SUBTYPE_UNKNOWN),
        req.lymph_nodes_positive,
    ]], dtype=float)


def _heuristic_probability(req: ERPredictRequest) -> float:
    """Transparent fallback: lower grade / fewer nodes lean ER-positive."""
    score = 0.5
    score += 0.12 if req.histologic_grade == 1 else (-0.12 if req.histologic_grade == 3 else 0)
    score += 0.10 if req.menopausal_state == "Post" else -0.05
    score -= 0.03 * min(req.lymph_nodes_positive, 5)
    score -= 0.02 if req.tumor_size > 30 else 0
    return float(min(max(score, 0.05), 0.95))


def predict(req: ERPredictRequest) -> ERPredictResponse:
    model, scaler = get_er_artifacts()

    if model is not None:
        X = _encode(req)
        if scaler is not None:
            X = scaler.transform(X)
        prob_pos = float(model.predict_proba(X)[0][1])
        version = "ensemble-v1"
    else:
        prob_pos = _heuristic_probability(req)
        version = "stub-heuristic"

    er_positive = prob_pos >= 0.5
    confidence = _confidence_band(prob_pos)
    return ERPredictResponse(
        case_id=req.case_id,
        er_result="ER Positive" if er_positive else "ER Negative",
        confidence=confidence,
        probability_positive=round(prob_pos, 4),
        probability_negative=round(1 - prob_pos, 4),
        model_version=version,
        recommendation=_recommendation(er_positive, confidence),
        treatment_signal=_treatment_signal(er_positive),
        contributions=_contributions(req),
    )
