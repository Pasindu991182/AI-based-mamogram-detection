"""Tier 2 — Quantitative morphological feature extraction (OpenCV).

Measures the 6 radiomic features from the Tier 1 mask, and computes the
"worst-case" feature vector across the CC and MLO views for patient safety.
"""
import math
from typing import Optional

import cv2
import numpy as np

# The 6 features and which direction is clinically "worse".
# min -> lower value is more suspicious; max -> higher value is more suspicious.
WORST_DIRECTION = {
    "circularity": "min",        # less round = more suspicious
    "margin_integrity": "min",   # spiculated/irregular margins = more suspicious
    "orientation_index": "max",  # taller-than-wide handled via index magnitude
    "max_diameter": "max",       # larger lesion = more suspicious
    "contrast_ratio": "max",
    "density_score": "max",
}


def extract_features(mask_bin: np.ndarray, clahe_gray: np.ndarray) -> tuple[
    Optional[dict], Optional[dict]
]:
    """Return (radiomic_features, bounding_box) or (None, None) if no lesion."""
    contours, _ = cv2.findContours(
        mask_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        return None, None

    c = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)
    bbox = {"x": int(x), "y": int(y), "width": int(w), "height": int(h)}

    area = cv2.contourArea(c)
    perimeter = cv2.arcLength(c, True)
    if perimeter <= 0 or area <= 0:
        return None, bbox

    circularity = (4 * math.pi * area) / (perimeter ** 2)

    hull_area = cv2.contourArea(cv2.convexHull(c))
    margin_integrity = area / hull_area if hull_area > 0 else 0.0

    orientation_index = float(w) / h if h > 0 else 0.0

    max_diameter = 0.0
    if len(c) >= 5:
        _, (d1, d2), _ = cv2.fitEllipse(c)
        max_diameter = max(d1, d2)

    mask_bool = mask_bin > 0
    contrast_ratio = (
        abs(np.mean(clahe_gray[mask_bool]) - np.mean(clahe_gray[~mask_bool])) / 255.0
    )
    density_score = (area / (256 * 256)) * 100

    features = {
        "circularity": round(float(circularity), 4),
        "margin_integrity": round(float(margin_integrity), 4),
        "orientation_index": round(float(orientation_index), 4),
        "max_diameter": round(float(max_diameter), 2),
        "contrast_ratio": round(float(contrast_ratio), 4),
        "density_score": round(float(density_score), 2),
    }
    return features, bbox


def worst_case(feature_dicts: list[dict]) -> Optional[dict]:
    """Combine per-view features into a single worst-case vector."""
    valid = [f for f in feature_dicts if f]
    if not valid:
        return None
    result = {}
    for key, direction in WORST_DIRECTION.items():
        values = [f[key] for f in valid]
        result[key] = min(values) if direction == "min" else max(values)
    return result
