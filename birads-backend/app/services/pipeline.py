"""Orchestrates Tier 1 -> 2 -> 3 for one or both views and fuses results."""
from app.schemas.analysis import (
    AnalysisResponse,
    BoundingBox,
    RadiomicFeatures,
    ViewAnalysis,
)
from app.services import tier1_segmentation, tier2_features, tier3_birads
from app.utils.imaging import decode_upload


def analyze_view(contents: bytes, view_name: str, patient_age: float) -> ViewAnalysis:
    img = decode_upload(contents)

    seg = tier1_segmentation.segment(img)
    features, bbox = tier2_features.extract_features(seg.mask_bin, seg.clahe_gray)
    mass_detected = bbox is not None
    radiomic_features = RadiomicFeatures(**features) if features else None

    acr = tier3_birads.assess(img, patient_age)
    # BI-RADS is decided by the rule engine over the ACTUAL Tier 2 features for
    # this view, so a view with no segmented mass is never scored as
    # suspicious, and the category always matches its own "why" explanation.
    birads = tier3_birads.rule_based_birads(radiomic_features, mass_detected)

    return ViewAnalysis(
        view=view_name,
        predicted_class="Mass Detected" if mass_detected else "No Mass Detected",
        bounding_box=BoundingBox(**bbox) if bbox else None,
        radiomic_features=radiomic_features,
        overlay_image_base64=seg.overlay_base64,
        mask_image_base64=seg.mask_base64,
        predicted_acr=acr["predicted_acr"],
        birads_code=birads["birads_code"],
        birads_label=birads["risk_label"],
    )


def run(
    cc_bytes: bytes | None,
    mlo_bytes: bytes | None,
    patient_age: float,
) -> AnalysisResponse:
    views: list[ViewAnalysis] = []
    if cc_bytes:
        views.append(analyze_view(cc_bytes, "CC View", patient_age))
    if mlo_bytes:
        views.append(analyze_view(mlo_bytes, "MLO View", patient_age))

    # Worst-case feature fusion (Tier 2).
    feature_dicts = [
        v.radiomic_features.model_dump()
        for v in views
        if v.radiomic_features is not None
    ]
    worst = tier2_features.worst_case(feature_dicts)

    # Overall BI-RADS = the most severe across views.
    overall_code = max((v.birads_code or 0) for v in views) if views else None
    overall_label = next(
        (v.birads_label for v in views if v.birads_code == overall_code), None
    )

    worst_features = RadiomicFeatures(**worst) if worst else None
    explanation = tier3_birads.build_explanation(worst_features, overall_code)

    return AnalysisResponse(
        status="success",
        patient_age=int(patient_age),
        worst_case_radiomics=worst_features,
        overall_birads_code=overall_code,
        overall_birads_label=overall_label,
        explanation=explanation,
        analyzed_views=views,
    )
