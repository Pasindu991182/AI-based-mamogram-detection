"""Unit tests for Case-Based Reasoning (CBR) engine."""
from app.services import cbr_engine


def test_cbr_benign_matching():
    # Benign-characteristic feature vector (high circularity & margin integrity)
    benign_feats = {
        "circularity": 0.88,
        "margin_integrity": 0.93,
        "orientation_index": 1.15,
        "max_diameter": 11.0,
        "contrast_ratio": 0.16,
        "density_score": 6.0,
    }
    result = cbr_engine.find_similar_cases(benign_feats, birads_code=2, top_k=3)
    assert len(result.matches) == 3
    assert result.malignant_count == 0
    assert result.benign_count == 3
    assert "100%" in result.biopsy_concordance
    assert "Benign" in result.biopsy_concordance
    assert "ACR BI-RADS 2 Concordance" in result.actionable_recommendation


def test_cbr_malignant_matching():
    # Malignant-characteristic feature vector (spiculated margins, low circularity, taller-than-wide)
    malignant_feats = {
        "circularity": 0.29,
        "margin_integrity": 0.45,
        "orientation_index": 0.65,
        "max_diameter": 28.0,
        "contrast_ratio": 0.35,
        "density_score": 25.0,
    }
    result = cbr_engine.find_similar_cases(malignant_feats, birads_code=5, top_k=3)
    assert len(result.matches) == 3
    assert result.malignant_count >= 2
    assert "Malignant" in result.biopsy_concordance
    assert "biopsy" in result.actionable_recommendation.lower()
