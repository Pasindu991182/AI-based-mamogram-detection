# INbreast AI Diagnostic System

An end-to-end research project for mammogram-based breast cancer decision support. This repository combines a FastAPI inference backend with a React dashboard frontend to analyze one or two mammogram views, generate AI segmentation masks, extract morphology indicators, predict breast density, and estimate BI-RADS-style risk levels.

## Overview

The system is built around a multi-stage workflow:

1. A user uploads a CC image, an MLO image, or both.
2. A ResNet50-UNet segmentation model detects suspicious regions and generates masks.
3. The backend extracts radiomic-style morphology signals from the predicted region.
4. A VGG16 feature extractor produces deep image embeddings.
5. An XGBoost model predicts ACR breast density.
6. A second XGBoost model combines image features, age, and density to estimate the final risk level.

The frontend presents two analysis modes:

- `Extract Morphology`: shows green overlay segmentation plus extracted clinical features.
- `Predict BI-RADS Risk`: shows black-and-white masks, predicted ACR density, and final risk classification.

## Key Features

- Multi-view mammogram analysis with optional CC and MLO uploads
- Mass segmentation with transparent green visualization overlays
- Morphology extraction from detected lesions
- Auto-ACR density prediction
- BI-RADS-oriented risk categorization
- Worst-case feature aggregation across multiple views
- Interactive browser UI plus Swagger API docs

## Repository Structure

```text
.
├── INbreast_MultiModal_Master.csv         # Research data/reference spreadsheet
├── INbreast_MultiModal_Master.numbers     # Numbers version of the reference sheet
├── backend/                               # FastAPI inference service
│   ├── api/routes.py
│   ├── core/config.py
│   ├── models/predictor.py
│   ├── services/risk_assessment.py
│   ├── utils/image_processing.py
│   ├── main.py
│   ├── requirements.txt
│   ├── resnet50_unet_inbreast_final.keras
│   ├── xgboost_model.pkl
│   ├── scaler.pkl
│   ├── acr_xgb_model.pkl
│   └── acr_scaler.pkl
├── frontend/                              # React + Vite dashboard
│   ├── src/pages/Dashboard.jsx
│   ├── src/services/api.js
│   ├── package.json
│   └── vite.config.js
└── readme.md                              # Root project documentation
```

## Tech Stack

### Frontend

- React 19
- Vite 8
- Tailwind CSS 4
- Axios
- React Icons

### Backend

- FastAPI
- Uvicorn
- TensorFlow / Keras
- VGG16
- XGBoost
- Scikit-learn
- OpenCV
- NumPy

## Architecture

### Frontend Flow

The frontend is a single dashboard page that:

- accepts CC and MLO uploads
- captures patient age
- calls `POST /segment_only` for morphology analysis
- calls `POST /predict` for risk prediction
- renders overlay images, binary masks, radiomic features, ACR density, and final risk output

### Backend Flow

The backend loads all AI artifacts at startup and exposes two endpoints:

- `POST /segment_only`
  - accepts one or two image files
  - returns green overlay masks, bounding boxes, per-view morphology values, and worst-case aggregated features
- `POST /predict`
  - accepts patient age plus one or two image files
  - returns per-view predictions, predicted ACR density, segmentation masks, and overall risk level

### Model Pipeline

- Segmentation model: `resnet50_unet_inbreast_final.keras`
- Feature extractor: `VGG16(weights="imagenet", include_top=False, pooling="avg")`
- ACR density model: `acr_xgb_model.pkl` + `acr_scaler.pkl`
- Risk model: `xgboost_model.pkl` + `scaler.pkl`

## Local Setup

### Prerequisites

- Python 3.11 recommended
- Node.js 18+ recommended
- npm
- Enough RAM for TensorFlow model loading

Because the backend uses TensorFlow and compiled scientific packages, a Conda environment is the safest option, especially on Apple Silicon.

### 1. Start the Backend

```bash
cd backend
conda create -n inbreast-ai python=3.11 -y
conda activate inbreast-ai
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Backend URLs:

- API root: [http://localhost:8000](http://localhost:8000)
- Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)

Notes:

- The backend loads all ML models during startup, so the first boot can take a little time.
- `VGG16(weights="imagenet")` may download pretrained ImageNet weights the first time if they are not already cached on the machine.

### 2. Start the Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

- App: [http://localhost:5173](http://localhost:5173)

## How To Use

1. Start the backend server.
2. Start the frontend dev server.
3. Open the dashboard in the browser.
4. Upload a CC image, an MLO image, or both.
5. Enter the patient age.
6. Choose one of the analysis actions:
   - `Extract Morphology` for green overlay segmentation and morphology values
   - `Predict BI-RADS Risk` for density prediction, binary masks, and overall risk assessment

## API Reference

### `GET /`

Health-style root endpoint.

Response:

```json
{
  "message": "Enterprise API is Running! Go to http://localhost:8000/docs"
}
```

### `POST /segment_only`

Analyzes uploaded images for segmentation and morphology extraction.

Form fields:

- `file_cc`: optional image file
- `file_mlo`: optional image file

Behavior:

- At least one file is required.
- Returns per-view segmentation overlays and worst-case aggregated morphology features.

Example:

```bash
curl -X POST "http://localhost:8000/segment_only" \
  -F "file_cc=@/absolute/path/to/cc-image.png" \
  -F "file_mlo=@/absolute/path/to/mlo-image.png"
```

### `POST /predict`

Runs the full density + risk prediction pipeline.

Form fields:

- `patient_age`: required number
- `file_cc`: optional image file
- `file_mlo`: optional image file

Behavior:

- At least one image is required.
- The overall result uses the highest-risk prediction across submitted views.

Example:

```bash
curl -X POST "http://localhost:8000/predict" \
  -F "patient_age=50" \
  -F "file_cc=@/absolute/path/to/cc-image.png" \
  -F "file_mlo=@/absolute/path/to/mlo-image.png"
```

## Output Summary

### Morphology Endpoint Returns

- `overlay_image_base64`
- `bounding_box`
- `radiomic_features`
- `worst_case_radiomics`

### Risk Endpoint Returns

- `overall_prediction_code`
- `overall_risk_level`
- `analyzed_views`
- `ai_predicted_acr`
- `segmentation_mask_base64`

## Important Implementation Notes

- The frontend expects the backend at `http://localhost:8000`.
- That backend URL is currently hard-coded in both:
  - `frontend/src/services/api.js`
  - `frontend/src/pages/Dashboard.jsx`
- CORS is fully open in the current backend configuration.
- Model files are committed directly inside `backend/`.
- This repository currently focuses on inference and UI; training scripts, auth, and persistence are not included.

## Current Risk Labels

The backend maps model outputs to these labels:

- `0`: `Normal (BI-RADS 1, 2)`
- `1`: `Low Risk (BI-RADS 3)`
- `2`: `High Risk (BI-RADS 4, 5, 6)`

## Troubleshooting

### Backend fails to start

- Make sure you are running `uvicorn` from inside `backend/`.
- Verify Python 3.11 is active.
- Reinstall dependencies if TensorFlow, OpenCV, or XGBoost import errors appear.

### Frontend cannot reach the API

- Confirm the backend is running on port `8000`.
- Check that the browser can open [http://localhost:8000/docs](http://localhost:8000/docs).
- If you changed the backend host or port, update the hard-coded API URLs in the frontend.

### First request is slow

- This is expected when TensorFlow initializes or downloads VGG16 weights for the first time.

## Project Status

This repository appears to be a final-year research prototype focused on AI-assisted mammogram interpretation. It is best described as a local research/demo system rather than a production-hardened clinical platform.

## Credits

Developed by Pasindu Iroshan for a final-year research project on multi-modal AI-driven breast cancer risk assessment and decision support.