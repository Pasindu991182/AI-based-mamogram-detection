# BI-RADS Diagnostic Engine — Backend

Professional FastAPI backend for the Explainable BI-RADS Morphological Scoring
Engine. Implements a transparent, 6-tier clinical pipeline plus Google OAuth.

## Architecture (6 Tiers)

| Tier | What it does | Model / method | Endpoint |
|------|--------------|----------------|----------|
| 1 | Lesion segmentation → binary mask + green overlay | ResNet50-UNet (Keras) | `POST /api/v1/analyze` |
| 2 | 6 radiomic features + worst-case fusion (CC/MLO) | OpenCV | `POST /api/v1/analyze` |
| 3 | White-box BI-RADS category (1–5) from the measured features + ACR breast-density estimate | Rule engine over Tier 2 features · VGG16+XGBoost for ACR | `POST /api/v1/analyze` |
| 4 | Automated radiology report with an editable Impression | NLP (OpenAI LLM) → deterministic template fallback | `POST /api/v1/report/generate` |
| 5 | ER status prediction (ER+/ER−) from 7 clinical inputs | Trained ensemble (`.pkl`) → heuristic fallback | `POST /api/v1/er/predict` |
| 6 | Clinical RAG assistant (guideline Q&A) | LangChain + OpenAI + FAISS | `POST /api/v1/chat` |

Auth: `POST /api/v1/auth/google` (Google ID token → app JWT). All tier
endpoints require `Authorization: Bearer <jwt>`.

### How the pipeline runs (Tiers 1–3)

`POST /analyze` accepts CC and/or MLO images and, for each view, runs:

1. **Segmentation** (Tier 1) — the ResNet50-UNet produces a binary lesion mask
   and a green overlay for review.
2. **Feature extraction** (Tier 2) — OpenCV measures the 6 radiomic features
   from the mask. Across CC + MLO the **worst-case** value of each feature is
   kept for patient safety.
3. **BI-RADS** (Tier 3) — a deterministic **white-box rule engine** assigns the
   category directly from the measured Tier 2 features, so the score can never
   contradict its own "why" explanation:
   - **No lesion segmented on a view → BI-RADS 1 (Negative)**
   - Lesion found, no suspicious signs → BI-RADS 2 (Benign)
   - 1 sign → BI-RADS 3; 2–3 signs → BI-RADS 4; severe (spiculated + large) → BI-RADS 5
   - Signs (ACR Atlas thresholds): circularity < 0.50, margin integrity < 0.75,
     orientation < 0.90, diameter > 15 px.
   A separate VGG16 + XGBoost model additionally predicts the ACR breast-density
   band (this does **not** decide the BI-RADS category).

The overall case BI-RADS is the most severe across the analysed views.

### Explainability outputs

- `POST /analyze` returns an `explanation` object — the white-box **rules that
  fired** (e.g. `Circularity 0.41 < 0.50 → shape is Irregular`) plus
  **feature-importance** weights.
- `POST /report/generate` returns a structured `document` (patient metadata,
  feature table, BI-RADS rationale, ER table) plus an NLP-written `impression`
  and a `generator` tag (`nlp-<model>` when an OpenAI key is set, else `template`).
- `POST /er/predict` returns `treatment_signal` and signed `contributions`
  (which inputs pushed the prediction ER+ / ER−).
- `GET /cases` returns flattened worklist summary fields; `GET /cases/{id}/detail`
  returns the full case (stored images, features, report, ER) for the read-only
  Case View.

## Quick start

```bash
cd birads-backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then set GOOGLE_CLIENT_ID + JWT_SECRET (see .env below)
uvicorn app.main:app          # ⚠️ do NOT use --reload — see note below
```

Open http://localhost:8000/docs for interactive Swagger.

> ⚠️ **Do not run with `--reload`.** On macOS, TensorFlow crashes inside
> uvicorn's auto-reload worker while loading the Keras model — the process is
> killed and requests fail with *"Analysis failed."* Always start the server
> **without** `--reload`. When you change code, stop it (`Ctrl+C`) and restart
> manually. If port 8000 is stuck, free it with `lsof -ti:8000 | xargs kill -9`.

### Model weights (not in git)

Two trained files are too large for GitHub (100 MB limit) and are excluded via
`.gitignore`. Place them in `ml_weights/` before running Tiers 1 and 5:

| File | Size | Tier |
|------|------|------|
| `resnet50_unet_inbreast_final.keras` | 241 MB | 1 — segmentation |
| `er_ensemble.pkl` | 51 MB | 5 — ER prediction |

The small weights (`acr_scaler.pkl`, `acr_xgb_model.pkl`, `scaler.pkl`,
`xgboost_model.pkl`) ship in git and are already present.

### `.env` essentials

| Key | Purpose |
|-----|---------|
| `GOOGLE_CLIENT_ID` | Google OAuth Web Client ID (same as the frontend) |
| `JWT_SECRET` | App session-token signing secret |
| `OPENAI_API_KEY` | *(optional)* enables the NLP report Impression + Tier 6 assistant |
| `STORAGE_BACKEND` | `local` (default) or `cloudinary` |
| `CLOUDINARY_*` | *(optional)* persistent image storage; falls back to local disk |

## Image storage

On `POST /analyze` (for a saved case) the original CC/MLO images plus the
segmentation overlay and mask are uploaded via the storage backend and their
URLs saved on the case/analysis rows — so a case can be re-opened later with all
its images intact.

- `STORAGE_BACKEND=local` → files written to `uploads/`, served at `/uploads/...`
- `STORAGE_BACKEND=cloudinary` → uploaded to Cloudinary, permanent `https://res.cloudinary.com/...` URLs

Uploads never break the analysis — a storage failure is logged and the response
still returns.

## Tier 6 — Clinical RAG assistant

A conversational assistant that answers **only from loaded guideline documents**
(BI-RADS lexicon, NCCN patient guidelines, ASCO/CAP HER2, Sri Lanka NCCP, …),
with per-session memory and source citations. Available as a floating chat
widget on every frontend page.

**Setup (one-time):**

```bash
# 1. deps are in requirements.txt (langchain, langchain-openai, faiss-cpu, pypdf, …)
pip install -r requirements.txt

# 2. add your key to .env
OPENAI_API_KEY=sk-...

# 3. build the FAISS knowledge-base index (downloads PDFs + embeds; ~$0.02)
python -m scripts.build_rag_index
```

- `GET  /api/v1/chat/status` — readiness (`key_configured`, `index_ready`, `ready`).
- `POST /api/v1/chat` — `{message, session_id, case_id?}` → `{answer, sources}`.
  Pass `case_id` to ground answers in that case's live BI-RADS / ER values.
- Add your own docs (e.g. generated reports) to `rag_docs/`, edit
  `app/services/rag/knowledge_sources.py`, then re-run the build script.
- The chat endpoint returns HTTP 503 with a clear message until the key is set
  and the index is built — the app boots fine either way.

> ⚠️ Clinical safety: this is a document-Q&A aid, not a diagnostic authority.
> It says "I don't know" when the answer isn't in the documents. Keep a
> clinician in the loop.

## API summary

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/auth/google` | Google ID token → app JWT |
| GET  | `/api/v1/auth/me` | Current user |
| POST | `/api/v1/analyze` | Tiers 1–3 (segment, features, BI-RADS) |
| POST | `/api/v1/report/generate` | Tier 4 report (NLP Impression) |
| PUT  | `/api/v1/report/{id}` | Save / finalize (sign off) a report |
| POST | `/api/v1/er/predict` | Tier 5 ER-status prediction |
| POST | `/api/v1/chat` · GET `/api/v1/chat/status` | Tier 6 assistant |
| GET/POST | `/api/v1/cases` | List (filter by `patient_ref`) / create |
| GET | `/api/v1/cases/{id}` · `/api/v1/cases/{id}/detail` | Summary / full detail |
| PATCH / DELETE | `/api/v1/cases/{id}` | Edit patient / delete case (cascades) |

## Project layout

```
app/
├── main.py              # app, CORS, static uploads, lifespan
├── core/                # config, security (JWT + Google), logging
├── api/v1/              # auth, analyze, report, er_status, cases, chat
├── services/            # tier1..tier5 + pipeline + nlp_report + model_registry
│   └── rag/             # Tier 6: engine, ingest, knowledge_sources
├── models/  schemas/    # SQLAlchemy tables + Pydantic contracts
├── db/                  # engine, session, base
├── storage/             # local + cloudinary (swap via STORAGE_BACKEND)
└── utils/imaging.py
ml_weights/              # trained .keras + .pkl artefacts (large ones .gitignored)
scripts/                 # build_rag_index.py
alembic/                 # migrations
```

## Database

SQLite by default (`birads.db`). Tables auto-create on startup for dev.
For production, switch `DATABASE_URL` to Postgres and use Alembic:

```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

Schema: `users → cases → { analyses, reports, er_predictions }` with foreign
keys and cascade-delete (deleting a case removes its analysis, report and ER row).

## Tier 4 / Tier 5 model notes

- **Tier 4 (report):** the Impression is written by an OpenAI LLM when
  `OPENAI_API_KEY` is set; otherwise a deterministic clinical template is used.
  See `app/services/nlp_report.py`.
- **Tier 5 (ER):** if `er_ensemble.pkl` (+ optional `er_scaler.pkl`) is present
  in `ml_weights/`, the trained ensemble is used; otherwise a transparent
  heuristic fallback keeps the pipeline working. No code change to swap.

## Tests

```bash
pytest -q          # smoke tests run without the heavy Keras/ensemble models
```

> Note: the trained imaging models are **ResNet50-UNet** and **XGBoost**
> (not Attention U-Net / Random Forest). Keep your report wording aligned
> with the actual architecture, or retrain to match.
