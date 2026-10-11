"""Tier 4 — Automated radiology report generation.

Builds a structured, professional mammography report from the tier outputs and
generates the Impression via NLP (LLM, with a deterministic template fallback).
"""
from datetime import date

from app.schemas.analysis import RadiomicFeatures
from app.schemas.report import (
    BiRadsSection,
    FeatureRow,
    MetaItem,
    ReportDocument,
    ReportERInfo,
    ReportPatientMeta,
)
from app.services import nlp_report

BIRADS_MEANING = {
    1: ("BI-RADS 1 (negative)", "Negative — no abnormality.", "Routine screening."),
    2: ("BI-RADS 2 (benign)", "Benign finding.", "Routine screening."),
    3: ("BI-RADS 3 (probably benign)", "Probably benign finding.",
        "Short-interval (6-month) follow-up."),
    4: ("BI-RADS 4 (suspicious abnormality)", "Suspicious abnormality.",
        "Tissue biopsy is recommended."),
    5: ("BI-RADS 5 (highly suggestive of malignancy)",
        "Highly suggestive of malignancy.",
        "Biopsy and clinical correlation strongly recommended."),
}


# --- Feature interpretation (Tier 2 → human-readable table) ---------------
def feature_rows(f: RadiomicFeatures) -> list[FeatureRow]:
    # Circularity
    if f.circularity >= 0.75:
        circ = "Round / oval shape"
    elif f.circularity >= 0.5:
        circ = "Mildly irregular shape"
    else:
        circ = "Irregular shape"

    # Margin (derived from margin_integrity: lower integrity = more variance)
    if f.margin_integrity >= 0.9:
        margin_val, margin_int = "Low", "Circumscribed margins"
    elif f.margin_integrity >= 0.75:
        margin_val, margin_int = "Moderate", "Lobulated margins"
    else:
        margin_val, margin_int = "High", "Spiculated margins"

    # Orientation (width/height < 0.9 ⇒ taller-than-wide)
    if f.orientation_index < 0.9:
        orient_val, orient_int = "Vertical", "Taller-than-wide"
    else:
        orient_val, orient_int = "Horizontal", "Parallel to skin"

    # Contrast
    if f.contrast_ratio >= 0.25:
        contrast_val = "Elevated"
    elif f.contrast_ratio >= 0.1:
        contrast_val = "Moderate"
    else:
        contrast_val = "Low"

    # Density %
    if f.density_score >= 50:
        density_val = "High (heterogeneously dense)"
    elif f.density_score >= 25:
        density_val = "Moderate"
    else:
        density_val = "Low (predominantly fatty)"

    return [
        FeatureRow(feature="Circularity", value=f"{f.circularity:.2f}", interpretation=circ),
        FeatureRow(feature="Margin variance", value=margin_val, interpretation=margin_int),
        FeatureRow(feature="Orientation", value=orient_val, interpretation=orient_int),
        FeatureRow(feature="Diameter (max)", value=f"{f.max_diameter:.0f} px", interpretation="—"),
        FeatureRow(feature="Contrast", value=contrast_val,
                   interpretation="Distinct from surrounding tissue"),
        FeatureRow(feature="Density %", value=density_val, interpretation="—"),
    ]


def _birads_rationale(f: RadiomicFeatures, code: int) -> str:
    if code <= 2:
        return (
            "The lesion is round/oval with circumscribed margins and no suspicious "
            "features, consistent with a benign appearance under the ACR BI-RADS Atlas."
        )
    reasons = []
    if f.circularity < 0.5:
        reasons.append("the lesion shape is irregular (low circularity)")
    if f.margin_integrity < 0.75:
        reasons.append("the margins are spiculated")
    if f.orientation_index < 0.9:
        reasons.append("it shows a taller-than-wide orientation")
    joined = ", and ".join(reasons) if reasons else "the combined morphology is atypical"
    return (
        f"Rationale: {joined} — a combination associated with a higher suspicion "
        f"for malignancy under the ACR BI-RADS Atlas."
    )


def _default_meta(patient: ReportPatientMeta | None, views: str) -> list[MetaItem]:
    p = patient or ReportPatientMeta()
    return [
        MetaItem(label="Patient ID", value=p.patient_ref or "—"),
        MetaItem(label="Study date", value=p.study_date or date.today().isoformat()),
        MetaItem(label="Age", value=str(p.age) if p.age is not None else "—"),
        MetaItem(label="Modality", value=f"Digital Mammography ({views or 'CC + MLO'})"),
        MetaItem(label="Laterality", value=p.laterality or "Not specified"),
        MetaItem(label="Menopausal state", value=p.menopausal_state or "—"),
        MetaItem(label="Referring facility", value=p.referring_facility or "—"),
        MetaItem(label="Report type", value="Auto-generated (system)"),
    ]


def _template_impression(f, code, label, recommendation, er) -> str:
    density = "highly dense" if f.density_score >= 50 else "moderately dense"
    shape = "irregularly shaped" if f.circularity < 0.5 else "round/oval"
    margins = "spiculated margins" if f.margin_integrity < 0.75 else "circumscribed margins"
    er_clause = ""
    if er is not None:
        pct = round(er.probability_positive * 100)
        er_clause = (
            f" The predicted receptor status is {er.er_result.lower()} "
            f"({pct}% probability), which — if confirmed by IHC — would support "
            f"consideration of {'endocrine (hormone) therapy' if 'Positive' in er.er_result else 'chemotherapy pathways'} "
            f"in the treatment plan."
        )
    return (
        f"A {density}, {shape} lesion with {margins} is detected. "
        f"The lesion is assigned {label}, {recommendation.lower().rstrip('.')}."
        f"{er_clause} Tissue biopsy is recommended for definitive diagnosis."
    )


def build_report(
    features: RadiomicFeatures,
    birads_code: int,
    predicted_class: str = "Mass Detected",
    patient: ReportPatientMeta | None = None,
    er: ReportERInfo | None = None,
    views: str = "CC + MLO",
) -> dict:
    """Return {document, impression, generated_text, generator}."""
    code = birads_code if birads_code in BIRADS_MEANING else 4
    label, meaning, recommendation = BIRADS_MEANING[code]

    mass = predicted_class == "Mass Detected"
    segmentation = (
        "A suspicious lesion was segmented and its binary mask fused across the "
        "available CC and MLO views. The worst-case morphology across views is "
        "carried forward."
        if mass else
        "No suspicious mass or architectural distortion was segmented on the "
        "analysed views."
    )

    rows = feature_rows(features) if mass else []
    rationale = _birads_rationale(features, code)

    # --- NLP Impression (LLM with template fallback) ---
    context = _build_context(features, label, meaning, recommendation, er, mass)
    fallback = (
        _template_impression(features, code, label, recommendation, er)
        if mass else
        f"No suspicious finding identified. {label} — {meaning} {recommendation}"
    )
    impression, generator = nlp_report.generate_impression_nlp(context, fallback)

    document = ReportDocument(
        meta=_default_meta(patient, views),
        segmentation=segmentation,
        features=rows,
        birads=BiRadsSection(category=label, rationale=rationale,
                             recommendation=recommendation),
        er=er,
        impression=impression,
    )

    return {
        "document": document,
        "impression": impression,
        "generated_text": _render_plaintext(document),
        "generator": generator,
    }


def _build_context(features, label, meaning, recommendation, er, mass) -> str:
    lines = [
        f"Mass detected: {'yes' if mass else 'no'}",
        f"Circularity: {features.circularity:.2f}",
        f"Margin integrity: {features.margin_integrity:.2f}",
        f"Orientation index (w/h): {features.orientation_index:.2f}",
        f"Max diameter: {features.max_diameter:.0f} px",
        f"Contrast ratio: {features.contrast_ratio:.2f}",
        f"Density score: {features.density_score:.0f}%",
        f"Assigned category: {label} — {meaning}",
        f"Recommended step: {recommendation}",
    ]
    if er is not None:
        lines.append(
            f"ER prediction: {er.er_result} "
            f"({round(er.probability_positive * 100)}% probability, {er.confidence} confidence)"
        )
    return "\n".join(lines)


def _render_plaintext(doc: ReportDocument) -> str:
    """Flatten the structured document to plain text (DB storage + print fallback)."""
    out = [doc.title.upper(), doc.subtitle, ""]
    for m in doc.meta:
        out.append(f"{m.label}: {m.value}")
    out += ["", "1. SEGMENTATION (Tier 1)", doc.segmentation, ""]
    if doc.features:
        out.append("2. MORPHOLOGICAL FEATURES (Tier 2)")
        for r in doc.features:
            out.append(f"   - {r.feature}: {r.value} ({r.interpretation})")
        out.append("")
    out += [
        "3. BI-RADS CLASSIFICATION (Tier 3)",
        f"   Assigned: {doc.birads.category}",
        f"   {doc.birads.rationale}",
        f"   Recommendation: {doc.birads.recommendation}",
        "",
    ]
    if doc.er is not None:
        out += [
            "4. ER STATUS PREDICTION (Tier 4)",
            f"   Prediction: {doc.er.er_result}",
            f"   Probability (ER+): {round(doc.er.probability_positive * 100)}%",
            f"   Confidence: {doc.er.confidence}",
            f"   Inputs: {doc.er.inputs_summary}",
            "",
        ]
    out += ["5. IMPRESSION", doc.impression]
    return "\n".join(out)


GENERATOR_NAME = "nlp"  # kept for backward-compat imports
