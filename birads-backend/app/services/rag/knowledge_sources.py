"""Curated clinical knowledge sources for the RAG assistant.

Only publicly downloadable, redistribution-friendly guideline material is
listed here. Add or remove entries freely, then rebuild the index with
`python -m scripts.build_rag_index`.
"""

# Guideline PDFs (direct download links).
PDF_URLS = [
    # ---- Sri Lanka national guidelines (most relevant to the deployment setting) ----
    "https://www.nccp.health.gov.lk/storage/post/pdfs/National%20Guidelines-%20Management%20of%20Breast%20Cancers%20in%20Sri%20Lanka.pdf",
    "https://www.nccp.health.gov.lk/storage/post/pdfs/Comprehensive%20breast%20care%20book%20new%202021%20new%2003-18.pdf",
    # ---- HER2 testing (ASCO/CAP 2023) ----
    "https://documents.cap.org/documents/her2_breast_update_sor_2023.pdf",
    "https://documents.cap.org/documents/her2_breast_update_algorithms_2023.pdf",
    # ---- NCCN Guidelines for Patients (free, directly downloadable) ----
    "https://www.nccn.org/patients/guidelines/content/PDF/breastcancerscreening-patient.pdf",
    "https://www.nccn.org/patients/guidelines/content/PDF/breast-invasive-patient.pdf",
    "https://www.nccn.org/patients/guidelines/content/PDF/stage_iv_breast-patient.pdf",
        # ---- WHO Global Breast Cancer Initiative ----
    "https://iris.who.int/bitstream/handle/10665/366385/9789240065987-eng.pdf?sequence=1",
    # ---- CAP Breast Biomarker Reporting ----
    "https://documents.cap.org/protocols/cp-breast-biomarker-20-1400.pdf",
]

# Guideline web pages (HTML).
WEB_URLS = [
    # ---- BI-RADS lexicon & categories (Tiers 1-3) ----
    "https://www.ncbi.nlm.nih.gov/books/NBK459169/",
    "https://radiopaedia.org/articles/breast-imaging-reporting-and-data-system-bi-rads-2",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2797737/",
    # ---- Receptor testing (Tier 5 ER prediction) ----
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10791807/",
        # ---- ACR BI-RADS ----
    "https://www.acr.org/Clinical-Resources/Clinical-Tools-and-Reference/Reporting-and-Data-Systems/BI-RADS",
    # ---- BI-RADS v2025: Mammography Updates ----
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC13266138/",
    # ---- BI-RADS: Advantages and Limitations ----
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC9935970/",
    # ---- Practical Guide to BI-RADS v2025 ----
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC13361901/",
    # ---- WHO Global Breast Cancer Initiative ----
    "https://www.who.int/initiatives/global-breast-cancer-initiative",
  # ---- ACR Digital Mammography Quality Control ----
    "https://www.acr.org/Accreditation/Resources/Digital-Mammography-QC-Manual",
    # ---- CAP Current Cancer Protocols ----
    "https://www.cap.org/protocols-and-guidelines/cancer-protocols/current-cancer-protocols/",
    # ---- USPSTF Breast Cancer Screening ----
    "https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/breast-cancer-screening",

]
