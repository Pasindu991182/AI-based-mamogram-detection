# BI-RADS Diagnostic Engine — Backend

Professional FastAPI backend for the Explainable BI-RADS Morphological Scoring
Engine. Implements a transparent, 6-tier clinical pipeline plus Google OAuth.

## Architecture (6 Tiers)

| Tier | What it does | Model | Endpoint |
|------|--------------|-------|----------|
| 1 | Lesion segmentation → mask + green overlay | ResNet50-UNet (Keras) | `POST /api/v1/analyze` |
| 2 | 6 radiomic features + worst-case fusion (CC/MLO) | OpenCV | `POST /api/v1/analyze` |
| 3 | BI-RADS classification + auto-ACR density | XGBoost + VGG16 | `POST /api/v1/analyze` |
| 4 | Automated radiology report | Template engine (swap → T5) | `POST /api/v1/report/generate` |
| 5 | ER status prediction | Heuristic stub (swap → ensemble) | `POST /api/v1/er/predict` |
| 6 | Clinical RAG assistant (guideline Q&A) | LangChain + OpenAI + FAISS | `POST /api/v1/chat` |

Auth: `POST /api/v1/auth/google` (Google ID token → app JWT). All tier
endpoints require `Authorization: Bearer <jwt>`.

### Explainability outputs (for the wireframe panels)

- `POST /analyze` returns an `explanation` object — the white-box **rules that
  fired** (e.g. `Circularity 0.41 < 0.50 → shape is Irregular`) plus
  **feature importance** weights — derived from the worst-case features.
- `POST /er/predict` returns `treatment_signal` and signed `contributions`
  (which inputs pushed the prediction ER+ / ER−).
- `GET /cases` returns flattened worklist summary fields (`views`,
  `birads_code`, `er_result`, `report_finalized`, …) via `CaseOut.from_case`.

## Quick start

```bash
cd birads-backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then set GOOGLE_CLIENT_ID + JWT_SECRET
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for interactive Swagger.

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

## Project layout

```
app/
├── main.py              # app, CORS, static uploads, lifespan
├── core/                # config, security (JWT + Google), logging
├── api/v1/              # auth, analyze, report, er_status, cases
├── services/            # tier1..tier5 + pipeline + model_registry
├── models/  schemas/    # SQLAlchemy tables + Pydantic contracts
├── db/                  # engine, session, base
├── storage/             # local + cloudinary (swap via STORAGE_BACKEND)
└── utils/imaging.py
ml_weights/              # trained .keras + .pkl artefacts
alembic/                 # migrations
```

## Database

SQLite by default (`birads.db`). Tables auto-create on startup for dev.
For production, switch `DATABASE_URL` to Postgres and use Alembic:

```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

## Swapping in real Tier 4 / Tier 5 models

- **Tier 4 (T5/GPT-2):** implement `generate_with_t5` in
  `app/services/tier4_report.py` and set `GENERATOR_NAME = "t5"`.
- **Tier 5 (ensemble):** drop `er_ensemble.pkl` (+ optional `er_scaler.pkl`)
  into `ml_weights/`. The service auto-detects and uses it — no code change.

## Tests

```bash
pytest -q          # smoke tests run without heavy models
```

> Note: the trained imaging models are **ResNet50-UNet** and **XGBoost**
> (not Attention U-Net / Random Forest). Keep your report wording aligned
> with the actual architecture, or retrain to match.
