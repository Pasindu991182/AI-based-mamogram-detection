"""Generate high-quality CBR reference cases dataset."""
import json
import os
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "app" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "cbr_reference_cases.json"

def make_svg(shape_type: str, is_malignant: bool) -> str:
    if shape_type == "round":
        contour = "M 50,22 C 65,22 78,35 78,50 C 78,65 65,78 50,78 C 35,78 22,65 22,50 C 22,35 35,22 50,22 Z"
    elif shape_type == "oval":
        contour = "M 50,28 C 72,28 84,38 84,50 C 84,62 72,72 50,72 C 28,72 16,62 16,50 C 16,38 28,28 50,28 Z"
    elif shape_type == "microlobulated":
        contour = "M 50,24 C 62,20 74,28 76,40 C 78,48 84,54 80,64 C 76,74 64,76 52,78 C 40,80 30,72 26,62 C 22,50 26,38 34,28 C 40,22 44,25 50,24 Z"
    elif shape_type == "spiculated_mild":
        contour = "M 50,20 L 55,30 L 68,22 L 67,36 L 80,38 L 72,48 L 82,58 L 68,62 L 72,74 L 58,72 L 50,82 L 42,70 L 28,74 L 32,60 L 20,54 L 28,44 L 18,34 L 32,32 L 36,20 L 46,28 Z"
    else:
        contour = "M 50,15 L 56,28 L 74,18 L 70,34 L 88,34 L 76,46 L 90,58 L 74,62 L 80,78 L 62,72 L 54,88 L 44,74 L 26,82 L 30,64 L 12,58 L 26,46 L 14,32 L 32,34 L 30,16 L 44,26 Z"

    stroke_color = "#10b981" if not is_malignant else "#f43f5e"
    fill_color = "rgba(255,255,255,0.7)" if not is_malignant else "rgba(255,255,255,0.85)"
    
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" class="w-full h-full rounded-lg bg-slate-900">
  <defs>
    <radialGradient id="bg-grad-{shape_type}-{is_malignant}" cx="50%" cy="50%" r="60%">
      <stop offset="0%" stop-color="#334155" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#0f172a" stop-opacity="1"/>
    </radialGradient>
  </defs>
  <rect width="100" height="100" fill="url(#bg-grad-{shape_type}-{is_malignant})"/>
  <circle cx="50" cy="50" r="45" stroke="#475569" stroke-width="0.75" stroke-dasharray="2 3" fill="none"/>
  <path d="{contour}" fill="{fill_color}" stroke="{stroke_color}" stroke-width="2.5" stroke-linejoin="round"/>
</svg>"""

CASES = [
    # BI-RADS 2 - Benign cases
    {
        "case_id": "HIST-2023-014",
        "patient_age": 52,
        "ground_truth_birads": 2,
        "ground_truth_label": "BI-RADS 2 (Benign)",
        "biopsy_outcome": "Simple Breast Cyst (Benign)",
        "is_malignant": False,
        "er_status": "N/A (Benign)",
        "clinical_action_taken": "Aspiration performed; routine 12-month annual screening mammography.",
        "key_morphology": "Circumscribed margins, high circularity, smooth boundary",
        "features": {
            "circularity": 0.89,
            "margin_integrity": 0.94,
            "orientation_index": 1.12,
            "max_diameter": 11.4,
            "contrast_ratio": 0.16,
            "density_score": 6.2,
        },
        "thumbnail_svg": make_svg("round", False),
    },
    {
        "case_id": "HIST-2023-028",
        "patient_age": 48,
        "ground_truth_birads": 2,
        "ground_truth_label": "BI-RADS 2 (Benign)",
        "biopsy_outcome": "Fibroadenoma (Benign)",
        "is_malignant": False,
        "er_status": "N/A (Benign)",
        "clinical_action_taken": "Ultrasound core biopsy confirmed benign fibroadenoma with no atypia.",
        "key_morphology": "Well-circumscribed oval mass oriented parallel to skin",
        "features": {
            "circularity": 0.86,
            "margin_integrity": 0.91,
            "orientation_index": 1.25,
            "max_diameter": 14.2,
            "contrast_ratio": 0.19,
            "density_score": 8.5,
        },
        "thumbnail_svg": make_svg("oval", False),
    },
    {
        "case_id": "HIST-2023-041",
        "patient_age": 56,
        "ground_truth_birads": 2,
        "ground_truth_label": "BI-RADS 2 (Benign)",
        "biopsy_outcome": "Hyalinized Involuting Fibroadenoma (Benign)",
        "is_malignant": False,
        "er_status": "N/A (Benign)",
        "clinical_action_taken": "Mammographic stability confirmed at 2-year follow-up; regular screening.",
        "key_morphology": "Smooth margins, popcorn coarse calcification, low-to-moderate contrast",
        "features": {
            "circularity": 0.84,
            "margin_integrity": 0.89,
            "orientation_index": 1.05,
            "max_diameter": 12.8,
            "contrast_ratio": 0.18,
            "density_score": 7.1,
        },
        "thumbnail_svg": make_svg("oval", False),
    },
    {
        "case_id": "HIST-2023-059",
        "patient_age": 61,
        "ground_truth_birads": 2,
        "ground_truth_label": "BI-RADS 2 (Benign)",
        "biopsy_outcome": "Intramammary Lymph Node (Benign)",
        "is_malignant": False,
        "er_status": "N/A (Benign)",
        "clinical_action_taken": "Typical radiolucent fatty hilum observed; discharge to routine recall.",
        "key_morphology": "Reniform circumscribed shape with central fatty notch",
        "features": {
            "circularity": 0.85,
            "margin_integrity": 0.93,
            "orientation_index": 1.35,
            "max_diameter": 9.2,
            "contrast_ratio": 0.14,
            "density_score": 4.8,
        },
        "thumbnail_svg": make_svg("round", False),
    },
    # BI-RADS 3 - Probably Benign
    {
        "case_id": "HIST-2023-075",
        "patient_age": 44,
        "ground_truth_birads": 3,
        "ground_truth_label": "BI-RADS 3 (Probably Benign)",
        "biopsy_outcome": "Cellular Fibroadenoma (Benign)",
        "is_malignant": False,
        "er_status": "N/A (Benign)",
        "clinical_action_taken": "Short-interval 6-month surveillance mammogram; stable over 24 months.",
        "key_morphology": "Macrolobulated contour, circumscribed over >75% of circumference",
        "features": {
            "circularity": 0.72,
            "margin_integrity": 0.84,
            "orientation_index": 1.08,
            "max_diameter": 13.5,
            "contrast_ratio": 0.22,
            "density_score": 9.2,
        },
        "thumbnail_svg": make_svg("microlobulated", False),
    },
    {
        "case_id": "HIST-2023-088",
        "patient_age": 50,
        "ground_truth_birads": 3,
        "ground_truth_label": "BI-RADS 3 (Probably Benign)",
        "biopsy_outcome": "Complicated Cyst / Sclerosing Adenosis",
        "is_malignant": False,
        "er_status": "N/A (Benign)",
        "clinical_action_taken": "Targeted ultrasound correlation; repeat unilateral mammography at 6 months.",
        "key_morphology": "Partially obscured margin due to glandular parenchymal overlap",
        "features": {
            "circularity": 0.69,
            "margin_integrity": 0.82,
            "orientation_index": 0.96,
            "max_diameter": 11.0,
            "contrast_ratio": 0.20,
            "density_score": 8.0,
        },
        "thumbnail_svg": make_svg("microlobulated", False),
    },
    # BI-RADS 4A / 4B / 4C - Suspicious
    {
        "case_id": "HIST-2024-112",
        "patient_age": 53,
        "ground_truth_birads": 4,
        "ground_truth_label": "BI-RADS 4A (Low Suspicion)",
        "biopsy_outcome": "Atypical Ductal Hyperplasia (ADH - Borderline)",
        "is_malignant": False,
        "er_status": "ER+ (Low)",
        "clinical_action_taken": "Vacuum-assisted 11G stereotactic biopsy; diagnostic surgical excision.",
        "key_morphology": "Microlobulated margin, borderline circularity, indistinct anterior edge",
        "features": {
            "circularity": 0.58,
            "margin_integrity": 0.78,
            "orientation_index": 0.94,
            "max_diameter": 15.8,
            "contrast_ratio": 0.24,
            "density_score": 12.0,
        },
        "thumbnail_svg": make_svg("spiculated_mild", False),
    },
    {
        "case_id": "HIST-2024-129",
        "patient_age": 55,
        "ground_truth_birads": 4,
        "ground_truth_label": "BI-RADS 4B (Moderate Suspicion)",
        "biopsy_outcome": "Invasive Ductal Carcinoma, Grade 1 (Malignant)",
        "is_malignant": True,
        "er_status": "ER+ (Allred 7/8)",
        "clinical_action_taken": "14G core biopsy; breast-conserving lumpectomy with sentinel node biopsy.",
        "key_morphology": "Irregular contour, indistinct / micro-spiculated margins, elevated contrast",
        "features": {
            "circularity": 0.44,
            "margin_integrity": 0.68,
            "orientation_index": 0.84,
            "max_diameter": 18.5,
            "contrast_ratio": 0.28,
            "density_score": 15.5,
        },
        "thumbnail_svg": make_svg("spiculated_mild", True),
    },
    {
        "case_id": "HIST-2024-142",
        "patient_age": 58,
        "ground_truth_birads": 4,
        "ground_truth_label": "BI-RADS 4C (High Suspicion)",
        "biopsy_outcome": "Invasive Ductal Carcinoma, Grade 2 (Malignant)",
        "is_malignant": True,
        "er_status": "ER+ (Allred 8/8)",
        "clinical_action_taken": "Urgent 14G core biopsy; multidisciplinary oncology referral for neoadjuvant therapy.",
        "key_morphology": "Taller-than-wide orientation, focal spiculations, localized retraction",
        "features": {
            "circularity": 0.38,
            "margin_integrity": 0.62,
            "orientation_index": 0.76,
            "max_diameter": 22.0,
            "contrast_ratio": 0.32,
            "density_score": 18.4,
        },
        "thumbnail_svg": make_svg("spiculated_mild", True),
    },
    {
        "case_id": "HIST-2024-167",
        "patient_age": 64,
        "ground_truth_birads": 4,
        "ground_truth_label": "BI-RADS 4C (High Suspicion)",
        "biopsy_outcome": "Invasive Lobular Carcinoma (Malignant)",
        "is_malignant": True,
        "er_status": "ER+ (Strong)",
        "clinical_action_taken": "Core needle biopsy + breast MRI to evaluate bilateral extent; surgical consultation.",
        "key_morphology": "Ill-defined infiltrative borders, asymmetric parenchymal density",
        "features": {
            "circularity": 0.41,
            "margin_integrity": 0.59,
            "orientation_index": 0.78,
            "max_diameter": 24.5,
            "contrast_ratio": 0.30,
            "density_score": 21.0,
        },
        "thumbnail_svg": make_svg("spiculated_mild", True),
    },
    # BI-RADS 5 - Highly Suggestive of Malignancy
    {
        "case_id": "HIST-2024-205",
        "patient_age": 67,
        "ground_truth_birads": 5,
        "ground_truth_label": "BI-RADS 5 (Highly Suspicious)",
        "biopsy_outcome": "Invasive Ductal Carcinoma, Grade 3 (Malignant)",
        "is_malignant": True,
        "er_status": "ER- / HER2+ (Aggressive)",
        "clinical_action_taken": "Immediate core biopsy; staging CT and targeted HER2-directed chemotherapy.",
        "key_morphology": "Prominently spiculated stellate mass with radiating lines into Cooper ligaments",
        "features": {
            "circularity": 0.28,
            "margin_integrity": 0.44,
            "orientation_index": 0.64,
            "max_diameter": 29.0,
            "contrast_ratio": 0.36,
            "density_score": 26.5,
        },
        "thumbnail_svg": make_svg("spiculated_overt", True),
    },
    {
        "case_id": "HIST-2024-221",
        "patient_age": 71,
        "ground_truth_birads": 5,
        "ground_truth_label": "BI-RADS 5 (Highly Suspicious)",
        "biopsy_outcome": "Infiltrating Ductal Carcinoma with Necrosis (Malignant)",
        "is_malignant": True,
        "er_status": "Triple Negative (ER-/PR-/HER2-)",
        "clinical_action_taken": "Core biopsy confirmed high-grade TNBC; fast-track systemic oncology admission.",
        "key_morphology": "Markedly irregular dense mass, thick desmoplastic reaction",
        "features": {
            "circularity": 0.24,
            "margin_integrity": 0.39,
            "orientation_index": 0.58,
            "max_diameter": 34.0,
            "contrast_ratio": 0.40,
            "density_score": 32.0,
        },
        "thumbnail_svg": make_svg("spiculated_overt", True),
    },
]

if __name__ == "__main__":
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(CASES, f, indent=2)
    print(f"Generated {len(CASES)} cases in {OUT_FILE}")
