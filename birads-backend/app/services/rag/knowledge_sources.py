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
]

# Guideline web pages (HTML).
WEB_URLS = [
    # ---- BI-RADS lexicon & categories (Tiers 1-3) ----
    "https://www.ncbi.nlm.nih.gov/books/NBK459169/",
    "https://radiopaedia.org/articles/breast-imaging-reporting-and-data-system-bi-rads-2",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2797737/",
    # ---- Receptor testing (Tier 5 ER prediction) ----
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10791807/",
]
