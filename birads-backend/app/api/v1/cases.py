"""Patient case CRUD + history."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.case import Case
from app.models.user import User
from app.schemas.case import CaseCreate, CaseDetail, CaseOut, CaseUpdate

router = APIRouter(prefix="/cases", tags=["cases"])


def _owned_case(case_id: int, db: Session, user: User) -> Case:
    case = db.get(Case, case_id)
    if not case or case.owner_id != user.id:
        raise HTTPException(404, "Case not found.")
    return case


@router.post("", response_model=CaseOut, status_code=201)
def create_case(
    body: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = Case(
        owner_id=current_user.id,
        patient_ref=body.patient_ref,
        patient_age=body.patient_age,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return CaseOut.from_case(case)


@router.get("", response_model=list[CaseOut])
def list_cases(
    patient_ref: str | None = Query(None, description="Filter to one patient's history"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Case).filter(Case.owner_id == current_user.id)
    if patient_ref:
        query = query.filter(Case.patient_ref == patient_ref)
    cases = query.order_by(Case.created_at.desc()).all()
    return [CaseOut.from_case(c) for c in cases]


@router.get("/{case_id}", response_model=CaseOut)
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CaseOut.from_case(_owned_case(case_id, db, current_user))


@router.get("/{case_id}/detail", response_model=CaseDetail)
def get_case_detail(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Full read-only view: stored CC/MLO images, mask/overlay, features,
    BI-RADS, saved report text, and ER prediction — for the Worklist "View"
    action / patient history."""
    return CaseDetail.from_case(_owned_case(case_id, db, current_user))


@router.patch("/{case_id}", response_model=CaseOut)
def update_case(
    case_id: int,
    body: CaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = _owned_case(case_id, db, current_user)
    if body.patient_ref is not None:
        case.patient_ref = body.patient_ref
    if body.patient_age is not None:
        case.patient_age = body.patient_age
    db.commit()
    db.refresh(case)
    return CaseOut.from_case(case)


@router.delete("/{case_id}", status_code=204)
def delete_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = _owned_case(case_id, db, current_user)
    db.delete(case)  # cascades to analysis / report / er_prediction
    db.commit()
