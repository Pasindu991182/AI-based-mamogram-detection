"""Administrator-only: user provisioning, system overview and audit trail.

There is no public sign-up. Admin endpoints expose aggregate counts only —
never patient records.
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.api.v1.auth import is_locked, revoke_sessions
from app.core.logging import get_logger
from app.core.security import hash_password, password_policy_error
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.case import Case
from app.models.user import ROLE_ADMIN, RefreshToken, User
from app.schemas.auth import (
    AdminOverview,
    AdminPasswordReset,
    AdminUserCreate,
    AdminUserOut,
    AdminUserUpdate,
    AuditEntry,
)
from app.services import audit

logger = get_logger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


def _out(user: User, case_count: int = 0) -> AdminUserOut:
    return AdminUserOut(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        must_change_password=user.must_change_password,
        is_active=user.is_active,
        locked=is_locked(user),
        last_login_at=user.last_login_at,
        case_count=case_count,
    )


def _get_user(user_id: int, db: Session) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(404, "User not found.")
    return user


@router.get("/overview", response_model=AdminOverview)
def overview(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    now = datetime.now(timezone.utc)
    users = db.query(User).all()
    by_status = dict(db.query(Case.status, func.count(Case.id)).group_by(Case.status).all())
    return AdminOverview(
        users_total=len(users),
        users_active=sum(u.is_active for u in users),
        users_admin=sum(u.is_active and u.role == ROLE_ADMIN for u in users),
        users_locked=sum(is_locked(u) for u in users),
        users_pending_password=sum(u.is_active and u.must_change_password for u in users),
        sessions_active=db.query(RefreshToken)
        .filter(RefreshToken.revoked_at.is_(None), RefreshToken.expires_at > now)
        .count(),
        failed_logins_24h=db.query(AuditLog)
        .filter(
            AuditLog.action == audit.LOGIN_FAILED,
            AuditLog.created_at >= now - timedelta(hours=24),
        )
        .count(),
        cases_total=sum(by_status.values()),
        cases_by_status=by_status,
    )


@router.get("/audit", response_model=list[AuditEntry])
def audit_trail(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Most recent security events, newest first."""
    return (
        db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
    )


@router.get("/users", response_model=list[AdminUserOut])
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    counts = dict(
        db.query(Case.owner_id, func.count(Case.id)).group_by(Case.owner_id).all()
    )
    users = db.query(User).order_by(User.name, User.email).all()
    return [_out(u, counts.get(u.id, 0)) for u in users]


@router.post("/users", response_model=AdminUserOut, status_code=201)
def create_user(
    body: AdminUserCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(409, "A user with this email already exists.")
    problem = password_policy_error(body.password, body.email)
    if problem:
        raise HTTPException(400, problem)

    user = User(
        email=body.email,
        name=body.name.strip(),
        role=body.role,
        password_hash=hash_password(body.password),
        must_change_password=True,
    )
    db.add(user)
    audit.record(db, audit.USER_CREATED, actor=admin, target=user.email, request=request)
    db.commit()
    db.refresh(user)
    logger.info("Admin %s created user %s (%s)", admin.id, user.id, user.role)
    return _out(user)


@router.patch("/users/{user_id}", response_model=AdminUserOut)
def update_user(
    user_id: int,
    body: AdminUserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = _get_user(user_id, db)
    # An admin cannot lock themselves out of the only way to manage accounts.
    if user.id == admin.id and (
        body.is_active is False or (body.role is not None and body.role != ROLE_ADMIN)
    ):
        raise HTTPException(400, "You cannot deactivate or demote your own account.")

    if body.name is not None:
        user.name = body.name.strip()
    if body.role is not None:
        user.role = body.role
    action = audit.USER_UPDATED
    if body.is_active is not None and body.is_active != user.is_active:
        user.is_active = body.is_active
        action = audit.USER_REACTIVATED if body.is_active else audit.USER_DEACTIVATED
        if not body.is_active:
            revoke_sessions(db, user)
    audit.record(db, action, actor=admin, target=user.email, request=request)
    db.commit()
    db.refresh(user)
    logger.info("Admin %s updated user %s", admin.id, user.id)
    return _out(user)


@router.post("/users/{user_id}/reset-password", response_model=AdminUserOut)
def reset_password(
    user_id: int,
    body: AdminPasswordReset,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Issue a temporary password, sign the user out everywhere, clear lockout."""
    user = _get_user(user_id, db)
    problem = password_policy_error(body.password, user.email)
    if problem:
        raise HTTPException(400, problem)

    user.password_hash = hash_password(body.password)
    user.must_change_password = True
    user.failed_login_attempts = 0
    user.locked_until = None
    user.token_version += 1
    revoke_sessions(db, user)
    audit.record(db, audit.PASSWORD_RESET, actor=admin, target=user.email, request=request)
    db.commit()
    db.refresh(user)
    logger.info("Admin %s reset the password of user %s", admin.id, user.id)
    return _out(user)
