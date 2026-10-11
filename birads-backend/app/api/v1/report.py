"""Tier 4 endpoint: generate and edit the radiology report."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.case import Case
from app.models.report import Report
from app.models.user import User
from app.schemas.report import (
    ReportGenerateRequest,
    ReportResponse,
    ReportUpdateRequest,
)
from app.services import tier4_report

router = APIRouter(prefix="/report", tags=["report"])


@router.post("/generate", response_model=ReportResponse)
def generate(
    body: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    built = tier4_report.build_report(
        features=body.features,
        birads_code=body.birads_code,
        predicted_class=body.predicted_class,
        patient=body.patient,
        er=body.er,
    )

    report_id = None
    if body.case_id is not None:
        case = db.get(Case, body.case_id)
        if not case or case.owner_id != current_user.id:
            raise HTTPException(404, "Case not found.")
        report = case.report or Report(case_id=case.id)
        report.generated_text = built["generated_text"]
        report.generator = built["generator"]
        case.status = "reported"
        db.add(report)
        db.commit()
        db.refresh(report)
        report_id = report.id

    return ReportResponse(
        id=report_id,
        case_id=body.case_id,
        generator=built["generator"],
        impression=built["impression"],
        generated_text=built["generated_text"],
        document=built["document"],
    )


@router.put("/{report_id}", response_model=ReportResponse)
def update(
    report_id: int,
    body: ReportUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.get(Report, report_id)
    if not report or report.case.owner_id != current_user.id:
        raise HTTPException(404, "Report not found.")
    report.edited_text = body.edited_text
    if body.finalize:
        report.finalized_at = datetime.now(timezone.utc)
        report.case.status = "completed"
    db.commit()
    db.refresh(report)
    return ReportResponse.model_validate(report)
