"""Tier 5 endpoint: ER status prediction."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.case import Case
from app.models.er_prediction import ERPrediction
from app.models.user import User
from app.schemas.er_status import ERPredictRequest, ERPredictResponse
from app.services import tier5_er_status

router = APIRouter(prefix="/er", tags=["er-status"])


@router.post("/predict", response_model=ERPredictResponse)
def predict(
    body: ERPredictRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = tier5_er_status.predict(body)

    if body.case_id is not None:
        case = db.get(Case, body.case_id)
        if not case or case.owner_id != current_user.id:
            raise HTTPException(404, "Case not found.")
        record = case.er_prediction or ERPrediction(case_id=case.id)
        record.age = body.age
        record.tumor_size = body.tumor_size
        record.histologic_grade = body.histologic_grade
        record.cellularity = body.cellularity
        record.menopausal_state = body.menopausal_state
        record.histologic_subtype = body.histologic_subtype
        record.lymph_nodes_positive = body.lymph_nodes_positive
        record.er_result = result.er_result
        record.confidence = result.confidence
        record.probability_positive = result.probability_positive
        record.model_version = result.model_version
        db.add(record)
        db.commit()

    return result
