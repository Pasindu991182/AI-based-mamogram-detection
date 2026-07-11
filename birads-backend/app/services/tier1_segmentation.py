"""Tier 1 — Semantic segmentation of the lesion (ResNet50-UNet).

Produces a binary mask, a green overlay for clinician review, and the raw
mask array which Tier 2 consumes for morphological measurement.
"""
from dataclasses import dataclass

import cv2
import numpy as np

from app.services.model_registry import get_seg_model
from app.utils.imaging import png_to_base64, to_clahe_gray


@dataclass
class SegmentationResult:
    mask_bin: np.ndarray          # uint8 0/255 binary mask, 256x256
    clahe_gray: np.ndarray        # preprocessed grayscale used for measurement
    overlay_base64: str           # green-highlighted overlay (PNG b64)
    mask_base64: str              # black & white mask (PNG b64)
    has_lesion: bool


def segment(img: np.ndarray) -> SegmentationResult:
    seg_model = get_seg_model()

    clahe_gray = to_clahe_gray(img, size=256)
    rgb_input = cv2.cvtColor(clahe_gray, cv2.COLOR_GRAY2RGB).astype(np.float32) / 255.0

    pred = seg_model.predict(rgb_input[np.newaxis, ...], verbose=0)[0, :, :, 0]
    mask_bin = (pred > 0.5).astype(np.uint8) * 255

    # Green overlay for visual explainability.
    base_display = cv2.cvtColor(clahe_gray, cv2.COLOR_GRAY2BGR)
    green = np.zeros_like(base_display)
    green[:] = (0, 255, 0)
    green_area = cv2.bitwise_and(green, green, mask=mask_bin)
    blended = cv2.addWeighted(green_area, 0.4, base_display, 1.0, 0)

    return SegmentationResult(
        mask_bin=mask_bin,
        clahe_gray=clahe_gray,
        overlay_base64=png_to_base64(blended),
        mask_base64=png_to_base64(mask_bin),
        has_lesion=bool(mask_bin.any()),
    )
