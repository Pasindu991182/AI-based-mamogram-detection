"""Smoke tests that run without the heavy ML models or a Google client."""
from app.schemas.analysis import RadiomicFeatures
from app.schemas.er_status import ERPredictRequest
from app.services import tier4_report, tier5_er_status


def test_structured_report_high_suspicion():
    features = RadiomicFeatures(
        circularity=0.45,
        margin_integrity=0.62,
        orientation_index=0.8,
        max_diameter=24.0,
        contrast_ratio=0.35,
        density_score=55.0,
    )
    built = tier4_report.build_report(features, birads_code=4)
    doc = built["document"]
    # Structured sections are present…
    assert "BI-RADS 4" in doc.birads.category
    assert "spiculated" in doc.birads.rationale.lower()
    assert len(doc.features) == 6
    assert any(r.feature == "Circularity" for r in doc.features)
    # …and an impression + full plain-text rendering are produced.
    assert built["impression"]
    assert "IMPRESSION" in built["generated_text"]
    # Without an OpenAI key the generator falls back to the template.
    assert built["generator"] in ("template",) or built["generator"].startswith("nlp-")


def test_er_stub_returns_structured_result():
    req = ERPredictRequest(
        age=60,
        tumor_size=22.0,
        histologic_grade=1,
        cellularity="High",
        menopausal_state="Post",
        histologic_subtype="Ductal/NST",
        lymph_nodes_positive=0,
    )
    res = tier5_er_status.predict(req)
    assert res.er_result in ("ER Positive", "ER Negative")
    assert 0.0 <= res.probability_positive <= 1.0
    assert res.confidence in ("High", "Medium", "Low")
    # "stub-heuristic" when no model file is present (e.g. CI); "ensemble-v1"
    # when the trained er_ensemble.pkl has been dropped into ml_weights/.
    assert res.model_version in ("stub-heuristic", "ensemble-v1")
    assert res.treatment_signal
    assert res.contributions
