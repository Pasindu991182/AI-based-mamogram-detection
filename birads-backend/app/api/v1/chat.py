"""Tier 6 — Clinical RAG assistant endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.case import Case
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, ChatStatus
from app.services.rag import engine

router = APIRouter(prefix="/chat", tags=["assistant"])


@router.get("/status", response_model=ChatStatus)
def chat_status(current_user: User = Depends(get_current_user)):
    return ChatStatus(**engine.status())


@router.post("", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case_context = None
    if body.case_id is not None:
        case = db.get(Case, body.case_id)
        if not case or case.owner_id != current_user.id:
            raise HTTPException(404, "Case not found.")
        case_context = _build_case_context(case)

    try:
        result = engine.ask(
            question=body.message,
            session_id=body.session_id,
            case_context=case_context,
        )
    except engine.RAGNotReady as exc:
        raise HTTPException(503, str(exc))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(500, f"Assistant error: {exc}")

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        session_id=body.session_id,
    )


def _build_case_context(case: Case) -> str:
    """Flatten a case's tier outputs into a short context block for the LLM."""
    lines = [f"Patient ref: {case.patient_ref or 'N/A'}, age: {case.patient_age or 'N/A'}"]

    analysis = getattr(case, "analysis", None)
    if analysis is not None:
        if analysis.birads_code is not None:
            lines.append(
                f"BI-RADS: {analysis.birads_code} ({analysis.birads_label or ''})"
            )
        feats = {
            "circularity": analysis.circularity,
            "margin_integrity": analysis.margin_integrity,
            "orientation_index": analysis.orientation_index,
            "max_diameter": analysis.max_diameter,
            "contrast_ratio": analysis.contrast_ratio,
            "density_score": analysis.density_score,
        }
        present = {k: v for k, v in feats.items() if v is not None}
        if present:
            lines.append(
                "Morphology: "
                + ", ".join(f"{k}={v}" for k, v in present.items())
            )

    er = getattr(case, "er_prediction", None)
    if er is not None and er.er_result:
        lines.append(
            f"ER prediction: {er.er_result} "
            f"(p+={er.probability_positive}, confidence={er.confidence})"
        )

    return "\n".join(lines)
