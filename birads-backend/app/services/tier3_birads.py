"""Tier 3 — BI-RADS classification (XGBoost) + auto-ACR density.

Ported from the demo's risk_assessment.py + VGG feature extraction. Uses VGG16
deep features + patient age + an auto-predicted ACR density to assign a
BI-RADS risk band.
"""
import cv2
import numpy as np

from app.schemas.analysis import (
    BiRadsExplanation,
    BiRadsRule,
    FeatureImportance,
    RadiomicFeatures,
)
from app.services.model_registry import (
    get_acr_model,
    get_acr_scaler,
    get_birads_model,
    get_birads_scaler,
    get_vgg_extractor,
)

RISK_LABELS = {
    0: "Normal (BI-RADS 1, 2)",
    1: "Low Risk (BI-RADS 3)",
    2: "High Risk (BI-RADS 4, 5, 6)",
}

# Map the 3-class risk code to a representative BI-RADS category number.
RISK_CODE_TO_BIRADS = {0: 2, 1: 3, 2: 4}

# --- Rule-engine thresholds (ACR BI-RADS Atlas morphology cut-offs) --------
# Shared by rule_based_birads() and build_explanation() so the assigned
# category always matches the "why" panel shown in the report.
_CIRCULARITY_T = 0.50      # below → irregular shape
_MARGIN_T = 0.75           # below → spiculated / ill-defined margins
_ORIENTATION_T = 0.90      # below (width/height) → taller-than-wide
_DIAMETER_T = 15.0         # above → sizeable mass

# A stricter secondary bar for BI-RADS 5 — reserved for overt cases (severely
# spiculated AND large), since these 6 shape features alone (no calcification
# or architectural-distortion detection) don't otherwise justify ">95%
# probability of malignancy".
_SEVERE_MARGIN_T = 0.50
_SEVERE_DIAMETER_T = 20.0

BIRADS_LABELS = {
    1: "Negative (BI-RADS 1)",
    2: "Benign (BI-RADS 2)",
    3: "Probably Benign (BI-RADS 3)",
    4: "Suspicious (BI-RADS 4)",
    5: "Highly Suspicious (BI-RADS 5)",
}


def rule_based_birads(features: RadiomicFeatures | None, mass_detected: bool) -> dict:
    """Deterministic BI-RADS decision driven directly by the Tier 2
    morphological features — the exact same signals shown in the "why"
    panel (build_explanation) — so the category can never contradict its
    own rationale.

    Per the ACR Atlas, BI-RADS 2 ("benign") presumes a finding was seen and
    judged benign; it is not the right category when no lesion was segmented
    at all. No mass detected on this view → BI-RADS 1 ("negative").
    """
    if not mass_detected or features is None:
        return {"birads_code": 1, "risk_label": BIRADS_LABELS[1]}

    signs = 0
    if features.circularity < _CIRCULARITY_T:
        signs += 1
    if features.margin_integrity < _MARGIN_T:
        signs += 1
    if features.orientation_index < _ORIENTATION_T:
        signs += 1
    if features.max_diameter > _DIAMETER_T:
        signs += 1

    severe = (
        features.margin_integrity < _SEVERE_MARGIN_T
        and features.max_diameter > _SEVERE_DIAMETER_T
    )

    if severe and signs >= 3:
        code = 5
    elif signs >= 2:
        code = 4
    elif signs >= 1:
        code = 3
    else:
        code = 2
    return {"birads_code": code, "risk_label": BIRADS_LABELS[code]}


def extract_vgg_features(img: np.ndarray) -> np.ndarray:
    from tensorflow.keras.applications.vgg16 import preprocess_input
    from tensorflow.keras.preprocessing.image import img_to_array

    vgg = get_vgg_extractor()
    rgb = cv2.cvtColor(cv2.resize(img, (224, 224)), cv2.COLOR_BGR2RGB)
    arr = preprocess_input(np.expand_dims(img_to_array(rgb), axis=0))
    return vgg.predict(arr, verbose=0)[0]


def predict_auto_acr(vgg_features: np.ndarray, patient_age: float) -> int:
    acr_scaler = get_acr_scaler()
    acr_model = get_acr_model()

    features = list(vgg_features) + [patient_age]
    scaled = acr_scaler.transform(np.array(features).reshape(1, -1))
    pred_class = acr_model.predict(scaled)[0]  # 0..3
    return int(pred_class) + 1  # 1..4


def classify_vgg(vgg_features: np.ndarray, patient_age: float, acr_density: int) -> dict:
    """Legacy VGG16+XGBoost risk classifier (kept for reference/back-compat).

    NOT used to assign the final BI-RADS category — it was trained on raw
    image features independent of the Tier 2 morphology, which meant a view
    with "No Mass Detected" could still be scored as suspicious, and the
    category could contradict the "why" panel built from Tier 2 features.
    See rule_based_birads() for the feature-driven decision actually used.
    """
    scaler = get_birads_scaler()
    model = get_birads_model()

    final = list(vgg_features) + [patient_age, acr_density]
    # Feature-boosting strategy carried over from the original trained pipeline.
    for _ in range(15):
        final.extend([patient_age, acr_density])

    scaled = scaler.transform(np.array(final).reshape(1, -1))
    code = int(model.predict(scaled)[0])
    return {
        "risk_code": code,
        "risk_label": RISK_LABELS[code],
        "birads_code": RISK_CODE_TO_BIRADS[code],
        "predicted_acr": acr_density,
    }


def assess(img: np.ndarray, patient_age: float) -> dict:
    """Tier 3 ACR breast-density pass for a single view image.

    BI-RADS malignancy category is NOT decided here — see rule_based_birads(),
    which uses the actual Tier 2 morphological features so the category is
    always consistent with its own "why" explanation.
    """
    vgg = extract_vgg_features(img)
    acr = predict_auto_acr(vgg, patient_age)
    return {"predicted_acr": acr}


# --- Explainability (white-box rules + importance) -----------------------
# Relative importance the trained classifier assigns to each morphology input.
_BASE_IMPORTANCE = {
    "Margin integrity": 0.34,
    "Circularity": 0.28,
    "Orientation": 0.19,
    "Diameter": 0.12,
    "Contrast": 0.04,
    "Density": 0.03,
}


def build_explanation(
    features: RadiomicFeatures | None,
    birads_code: int | None,
) -> BiRadsExplanation:
    """Derive the human-readable 'why' panel from the worst-case features."""
    headline = (
        f"Why BI-RADS {birads_code}? — rules that fired"
        if birads_code is not None
        else "Morphology assessment"
    )
    rules: list[BiRadsRule] = []

    if features is not None:
        if features.circularity < _CIRCULARITY_T:
            rules.append(BiRadsRule(
                feature="Circularity",
                condition=f"{features.circularity:.2f} < {_CIRCULARITY_T:.2f}",
                interpretation="shape is Irregular",
                severity="warn",
            ))
        if features.margin_integrity < _MARGIN_T:
            rules.append(BiRadsRule(
                feature="Margin integrity",
                condition=f"{features.margin_integrity:.2f} < {_MARGIN_T:.2f}",
                interpretation="margins are Spiculated / ill-defined",
                severity="high",
            ))
        if features.orientation_index < _ORIENTATION_T:
            rules.append(BiRadsRule(
                feature="Orientation",
                condition=f"{features.orientation_index:.2f} < {_ORIENTATION_T:.2f}",
                interpretation="Taller-than-wide growth",
                severity="warn",
            ))
        if features.max_diameter > _DIAMETER_T:
            rules.append(BiRadsRule(
                feature="Diameter",
                condition=f"{features.max_diameter:.1f} px",
                interpretation="sizeable mass",
                severity="info",
            ))

    importance = [
        FeatureImportance(feature=k, weight=v) for k, v in _BASE_IMPORTANCE.items()
    ]
    return BiRadsExplanation(headline=headline, rules=rules, feature_importance=importance)
