# ExBI-RADS Engine

**Explainable Breast-Cancer Decision Support, End to End**

A transparent, 6-tier AI pipeline that mirrors a radiologist's own reasoning — from mammogram segmentation to white-box BI-RADS scoring, hormone-receptor (ER) status prediction, an auto-generated radiology report, and a guideline-grounded clinical assistant. Every output is traceable to the rules and measurements that produced it — no black box between the pixels and the score.

> ⚠️ **Clinical safety notice.** This is a research prototype and a decision-support aid — **not** an autonomous diagnostic device and **not** a substitute for a qualified clinician. Every output must be reviewed and signed off by a radiologist before any clinical decision.

---

## The Pipeline

| Tier | Stage | What it does | Technology |
|------|-------|---------------|------------|
| 1 | **Segmentation** | Isolates the lesion from surrounding breast tissue, producing a binary mask | ResNet50-UNet (attention-gated) |
| 2 | **Feature extraction** | Measures 6 radiomic features (circularity, margin integrity, orientation, diameter, contrast, density) from the fused CC/MLO mask, taking the worst-case value for patient safety | OpenCV |
| 3 | **BI-RADS classification** | A deterministic, white-box rule engine assigns a BI-RADS category (1–5) and shows exactly which measured features fired the decision, aligned to the ACR BI-RADS Atlas | Rule engine over Tier 2 features |
| 4 | **Radiology report** | Auto-drafts a structured report with patient metadata, findings, and an editable, NLP-generated Impression | LLM (OpenAI) with deterministic template fallback |
| 5 | **ER-status prediction** | Predicts hormone-receptor status (ER+/ER−) from 7 routine clinical inputs — no immunohistochemistry (IHC) required — with confidence banding, so treatment planning can start while pathology is pending | XGBoost / ensemble classifier |
| 6 | **Clinical assistant** | A retrieval-augmented (RAG) chatbot grounded in BI-RADS guidelines and treatment literature, with source citations and per-session memory | LangChain + OpenAI + FAISS |

Every tier's output is stored against the patient case, so a radiologist can re-open any study later and see the full trail: original images → segmentation mask → measured features → BI-RADS rationale → ER prediction → signed report.

---

## Architecture

```
AI-based-mamogram-detection/
├── birads-backend/     FastAPI · SQLAlchemy · TensorFlow/Keras · XGBoost · LangChain
└── birads-frontend/    React 18 · Vite · Tailwind CSS v4 · Google OAuth
```

Two independently deployable services communicating over a REST API. Authentication is Google OAuth end to end — the frontend obtains a Google ID token, the backend verifies it and issues its own signed session token.

### Backend — `birads-backend/`

- **FastAPI** REST API with routers per tier (`/analyze`, `/report`, `/er-status`, `/chat`, `/cases`)
- **SQLAlchemy + Alembic** — SQLite for development, swappable to PostgreSQL for production via a single environment variable
- **Cloudinary** for persistent image storage (originals, segmentation masks, overlays)
- **Model weights** — a pretrained segmentation network, an ACR-density classifier, a BI-RADS-support classifier and an ER-status ensemble live in `ml_weights/` (large binary weights are `.gitignore`-excluded; see [Setup](#setup) below)

### Frontend — `birads-frontend/`

- **React 18 + Vite** SPA styled with **Tailwind CSS v4**
- **Google Sign-In** (`@react-oauth/google`) — every study is signed to a named, authenticated radiologist
- A guided, multi-step **Study wizard** (Upload → Segment → Features → BI-RADS → ER Status → Report)
- A **Worklist** with search/filter (by BI-RADS category, ER status, sign-off status), per-patient history, and case detail views
- **PDF export** (`jsPDF`) of the signed radiology report
- An in-app **clinical chat assistant** available on every screen

---

## Setup

### Prerequisites
- Python 3.11+ and Node 18+
- A Google Cloud OAuth 2.0 Web Client ID
- (Optional) An OpenAI API key — enables the NLP report Impression and the Tier 6 assistant; both gracefully fall back without it
- (Optional) A Cloudinary account — enables persistent image storage; falls back to local disk without it

### 1. Backend

```bash
cd birads-backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in GOOGLE_CLIENT_ID, JWT_SECRET, and (optionally) OPENAI_API_KEY / Cloudinary keys
uvicorn app.main:app --reload
```
API docs available at `http://localhost:8000/docs`.

> **Model weights not in this repo.** Two trained model files are too large for GitHub (100 MB hard limit) and are excluded via `.gitignore`. Download them separately and place them in `birads-backend/ml_weights/`:
>
> | File | Size | Used by | Download |
> |------|------|---------|----------|
> | `resnet50_unet_inbreast_final.keras` | 241 MB | Tier 1 — segmentation | *link TBD* |
> | `er_ensemble.pkl` | 51 MB | Tier 5 — ER-status prediction | *link TBD* |
>
> All other weights (`acr_scaler.pkl`, `acr_xgb_model.pkl`, `scaler.pkl`, `xgboost_model.pkl`) are small enough to ship in git and are already present in `birads-backend/ml_weights/`.

To enable the Tier 6 assistant, build the guideline knowledge base once:
```bash
python -m scripts.build_rag_index
```

### 2. Frontend

```bash
cd birads-frontend
npm install
cp .env.example .env        # set VITE_API_URL and VITE_GOOGLE_CLIENT_ID (same client ID as the backend)
npm run dev
```
App available at `http://localhost:5173`.

---

## Clinical Value

- **Mirrors clinical reasoning.** Every BI-RADS score traces back to the exact measured features that fired it — circularity, margin integrity, orientation, diameter — matched to the ACR BI-RADS Atlas thresholds. Nothing is a black box.
- **Built for under-resourced clinics.** Designed for settings with a shortage of radiologists: flag BI-RADS 4/5 cases early and refer them up the chain before a full radiologist review is available.
- **Zero-IHC-leakage triage.** ER-status prediction from routine hospital data already on hand, so hormone-therapy vs. chemotherapy planning can begin before immunohistochemistry results return — potentially saving days in the treatment pathway.

---

## Tech Stack

**Backend:** FastAPI · SQLAlchemy · Alembic · TensorFlow/Keras · OpenCV · scikit-learn · XGBoost · LangChain · FAISS · Cloudinary
**Frontend:** React 18 · Vite · Tailwind CSS v4 · React Router · jsPDF · Google OAuth

---

## Status

Final-year research project. Individual services (`birads-backend/README.md`, `birads-frontend/README.md`) contain deeper setup and API documentation.

**Research prototype · Not a medical device · © 2026 ExBI-RADS**
