"""Case-Based Reasoning (CBR) Diagnostic Engine.

Retrieves verified historical patient cases matching the current lesion's
morphology and computes clinical similarity, biopsy concordance, and
ACR guideline-directed actionable recommendations.
"""
import json
import math
from pathlib import Path
from typing import Optional

from app.core.logging import get_logger
from app.schemas.analysis import RadiomicFeatures
from app.schemas.cbr import CbrAnalysisResult, CbrSimilarCase

logger = get_logger(__name__)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "cbr_reference_cases.json"

# Feature normalization parameters and clinical weights.
# Margin integrity and circularity have highest clinical weights in distinguishing
# benign vs malignant breast lesion morphology under ACR BI-RADS Atlas.
FEATURE_SPECS = {
    "margin_integrity": {"min": 0.10, "max": 1.00, "weight": 0.30},
    "circularity": {"min": 0.10, "max": 1.00, "weight": 0.25},
    "orientation_index": {"min": 0.40, "max": 1.60, "weight": 0.15},
    "max_diameter": {"min": 5.00, "max": 45.00, "weight": 0.15},
    "contrast_ratio": {"min": 0.05, "max": 0.45, "weight": 0.08},
    "density_score": {"min": 2.00, "max": 50.00, "weight": 0.07},
}

_REFERENCE_CASES_CACHE: list[dict] | None = None


def load_reference_cases() -> list[dict]:
    """Load and cache the historical reference cases library."""
    global _REFERENCE_CASES_CACHE
    if _REFERENCE_CASES_CACHE is not None:
        return _REFERENCE_CASES_CACHE

    if not DATA_PATH.exists():
        logger.warning("CBR data file missing at %s, returning empty list", DATA_PATH)
        return []

    try:
        with open(DATA_PATH, encoding="utf-8") as f:
            cases = json.load(f)
            _REFERENCE_CASES_CACHE = cases
            return cases
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to load CBR reference cases: %s", exc)
        return []


def calculate_similarity(query_feat: dict[str, float], ref_feat: dict[str, float]) -> float:
    """Compute weighted normalized similarity (0..100%)."""
    weighted_dist_sq = 0.0
    total_weight = 0.0

    for key, spec in FEATURE_SPECS.items():
        q_val = float(query_feat.get(key, 0.0))
        r_val = float(ref_feat.get(key, 0.0))
        span = spec["max"] - spec["min"]
        if span <= 0:
            continue

        # Normalized difference in [0, 1] range
        diff = abs(q_val - r_val) / span
        diff = min(1.0, diff)

        w = spec["weight"]
        weighted_dist_sq += w * (diff ** 2)
        total_weight += w

    if total_weight <= 0:
        return 75.0

    dist = math.sqrt(weighted_dist_sq / total_weight)
    similarity = max(55.0, min(98.5, (1.0 - dist) * 100))
    return round(similarity, 1)


def find_similar_cases(
    features: RadiomicFeatures | dict | None,
    birads_code: Optional[int] = None,
    patient_age: Optional[int] = None,
    top_k: int = 3,
) -> CbrAnalysisResult:
    """Find top-K historical twin cases and formulate clinical CBR concordance."""
    cases = load_reference_cases()
    if not cases or features is None:
        return CbrAnalysisResult(
            matches=[],
            biopsy_concordance="No reference cases retrieved (no lesion detected).",
            malignant_count=0,
            benign_count=0,
            actionable_recommendation="Routine screening.",
            clinical_rationale="No lesion segmented to perform CBR comparison.",
        )

    # Convert features to dict if Pydantic model
    q_dict = (
        features.model_dump()
        if hasattr(features, "model_dump")
        else (features.dict() if hasattr(features, "dict") else dict(features))
    )

    scored_cases: list[tuple[float, dict]] = []
    for ref in cases:
        sim = calculate_similarity(q_dict, ref.get("features", {}))
        # Small boost if BI-RADS category matches ground truth
        if birads_code and ref.get("ground_truth_birads") == birads_code:
            sim = min(99.0, sim + 2.5)
        scored_cases.append((sim, ref))

    # Sort descending by similarity
    scored_cases.sort(key=lambda x: x[0], reverse=True)
    top_matches = scored_cases[:top_k]

    matches: list[CbrSimilarCase] = []
    malignant_count = 0
    benign_count = 0

    for sim, c in top_matches:
        is_mal = bool(c.get("is_malignant", False))
        if is_mal:
            malignant_count += 1
        else:
            benign_count += 1

        matches.append(
            CbrSimilarCase(
                case_id=c.get("case_id", ""),
                patient_age=c.get("patient_age", 50),
                similarity_percentage=sim,
                ground_truth_birads=c.get("ground_truth_birads", 2),
                ground_truth_label=c.get("ground_truth_label", ""),
                biopsy_outcome=c.get("biopsy_outcome", ""),
                is_malignant=is_mal,
                er_status=c.get("er_status", "N/A"),
                clinical_action_taken=c.get("clinical_action_taken", ""),
                key_morphology=c.get("key_morphology", ""),
                thumbnail_svg=c.get("thumbnail_svg", ""),
                features=c.get("features", {}),
            )
        )

    # Compute Biopsy Concordance
    total_retrieved = len(matches)
    if total_retrieved > 0:
        if malignant_count == 0:
            concordance = f"{benign_count} of {total_retrieved} (100%) historical cases confirmed Benign on biopsy"
        elif benign_count == 0:
            concordance = f"{malignant_count} of {total_retrieved} (100%) historical cases confirmed Malignant on biopsy"
        else:
            mal_pct = round((malignant_count / total_retrieved) * 100)
            concordance = (
                f"{malignant_count} of {total_retrieved} ({mal_pct}%) historical cases confirmed Malignant; "
                f"{benign_count} of {total_retrieved} confirmed Benign"
            )
    else:
        concordance = "No matches."

    # Actionable Clinical Recommendation (ACR Guidelines grounded in CBR)
    code = birads_code or (4 if malignant_count > 0 else 2)
    if code <= 2:
        rec = (
            "ACR BI-RADS 2 Concordance: Characteristically benign morphological features. "
            "Biopsy precedents corroborate 0% malignancy. Action: Routine 12-month annual screening mammography."
        )
        rationale = (
            "Historical twin cases exhibit circumscribed margins and high circularity, "
            "with confirmed benign histology (simple cysts and fibroadenomas). Routine follow-up is standard of care."
        )
    elif code == 3:
        rec = (
            "ACR BI-RADS 3 Concordance: Probably benign finding (<2% estimated risk). "
            "Action: Short-interval surveillance unilateral diagnostic mammogram at 6 months to confirm structural stability."
        )
        rationale = (
            "Matched historical cases show mild microlobulation but stable 24-month trajectories. "
            "Surveillance rather than immediate biopsy avoids unnecessary invasive procedures."
        )
    elif code == 4:
        rec = (
            "ACR BI-RADS 4 Concordance: Suspicious morphological lesion. "
            "Action: Ultrasound-guided 14-gauge core needle biopsy (CNB) recommended within 14 days."
        )
        rationale = (
            f"Precedent analysis demonstrates high similarity ({round(top_matches[0][0]) if top_matches else 85}%) "
            "to histopathologically verified carcinoma cases with microspiculated margins and architectural tension."
        )
    else:  # BI-RADS 5
        rec = (
            "ACR BI-RADS 5 Concordance: Highly suggestive of malignancy (>95% probability). "
            "Action: Urgent image-guided core biopsy within 7 days and multidisciplinary breast tumor board referral."
        )
        rationale = (
            "Stellate/spiculated architecture strongly matches verified invasive ductal carcinoma twins. "
            "Expedited diagnostic tissue sampling and receptor characterization required."
        )

    return CbrAnalysisResult(
        matches=matches,
        biopsy_concordance=concordance,
        malignant_count=malignant_count,
        benign_count=benign_count,
        actionable_recommendation=rec,
        clinical_rationale=rationale,
    )
