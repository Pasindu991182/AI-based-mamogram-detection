"""Email + password login → short-lived access JWT + revocable refresh session."""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.deps import get_authenticated_user
from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    hash_password,
    hash_refresh_token,
    new_refresh_token,
    password_needs_rehash,
    password_policy_error,
    verify_password,
)
from app.db.session import get_db
from app.models.user import RefreshToken, User
from app.services import audit
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    TokenResponse,
    UserOut,
)

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

# The refresh cookie is only ever sent to the auth endpoints.
_COOKIE_PATH = f"{settings.API_V1_PREFIX}/auth"

_INVALID_LOGIN = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password."
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _aware(dt: datetime | None) -> datetime | None:
    """SQLite hands back naive datetimes; they were stored as UTC."""
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def is_locked(user: User) -> bool:
    locked_until = _aware(user.locked_until)
    return locked_until is not None and locked_until > _now()


def revoke_sessions(db: Session, user: User, keep_id: int | None = None) -> None:
    """Revoke the user's refresh sessions (optionally sparing the current one)."""
    query = db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None)
    )
    if keep_id is not None:
        query = query.filter(RefreshToken.id != keep_id)
    query.update({RefreshToken.revoked_at: _now()}, synchronize_session=False)


def _token_response(user: User) -> TokenResponse:
    token = create_access_token(subject=str(user.id), extra={"tv": user.token_version})
    return TokenResponse(
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserOut.model_validate(user),
    )


def _set_refresh_cookie(response: Response, raw_token: str) -> None:
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=raw_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_HOURS * 3600,
        path=_COOKIE_PATH,
        httponly=True,                    # unreadable from JavaScript (XSS)
        secure=settings.is_production,    # HTTPS-only outside local development
        samesite="strict",                # never sent on cross-site requests (CSRF)
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        path=_COOKIE_PATH,
        httponly=True,
        secure=settings.is_production,
        samesite="strict",
    )


def _current_session(request: Request, db: Session) -> RefreshToken | None:
    raw = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not raw:
        return None
    session = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == hash_refresh_token(raw))
        .first()
    )
    if (
        session is None
        or session.revoked_at is not None
        or _aware(session.expires_at) <= _now()
        or not session.user.is_active
    ):
        return None
    return session


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == body.email).first()

    if user is not None and is_locked(user):
        logger.warning("Login blocked: account %s is locked", user.id)
        audit.record(db, audit.LOGIN_FAILED, actor=user, target="locked", request=request)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Try again later.",
        )

    # Always runs one Argon2 verification, even for an unknown email.
    password_ok = verify_password(body.password, user.password_hash if user else None)

    if user is None or not password_ok or not user.is_active:
        audit.record(
            db, audit.LOGIN_FAILED, actor=user, actor_email=body.email, request=request
        )
        if user is not None and not password_ok:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.MAX_FAILED_LOGINS:
                user.locked_until = _now() + timedelta(minutes=settings.LOCKOUT_MINUTES)
                user.failed_login_attempts = 0
                logger.warning("Account %s locked after repeated failures", user.id)
                audit.record(db, audit.ACCOUNT_LOCKED, actor=user, request=request)
        db.commit()
        raise _INVALID_LOGIN

    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = _now()
    audit.record(db, audit.LOGIN_SUCCESS, actor=user, request=request)
    if password_needs_rehash(user.password_hash):
        user.password_hash = hash_password(body.password)

    raw, token_hash = new_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=_now() + timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS),
            user_agent=(request.headers.get("user-agent") or "")[:255],
        )
    )
    db.commit()
    db.refresh(user)
    logger.info("User %s signed in", user.id)

    _set_refresh_cookie(response, raw)
    return _token_response(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, db: Session = Depends(get_db)):
    """Exchange the httpOnly refresh cookie for a fresh access token."""
    session = _current_session(request, db)
    if session is None:
        # Drop the dead cookie along with the 401.
        failure = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Session expired. Sign in again."},
        )
        _clear_refresh_cookie(failure)
        return failure
    return _token_response(session.user)


@router.post("/logout", status_code=204)
def logout(request: Request, db: Session = Depends(get_db)):
    session = _current_session(request, db)
    if session is not None:
        session.revoked_at = _now()
        audit.record(db, audit.LOGOUT, actor=session.user, request=request)
        db.commit()
        logger.info("User %s signed out", session.user_id)
    response = Response(status_code=204)
    _clear_refresh_cookie(response)
    return response


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_authenticated_user)):
    return UserOut.model_validate(current_user)


@router.post("/change-password", response_model=TokenResponse)
def change_password(
    body: ChangePasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(400, "Current password is incorrect.")
    if body.new_password == body.current_password:
        raise HTTPException(400, "New password must differ from the current one.")
    problem = password_policy_error(body.new_password, current_user.email)
    if problem:
        raise HTTPException(400, problem)

    current_user.password_hash = hash_password(body.new_password)
    current_user.must_change_password = False
    current_user.token_version += 1

    # Sign every other browser out; this one keeps its session.
    session = _current_session(request, db)
    revoke_sessions(db, current_user, keep_id=session.id if session else None)
    audit.record(db, audit.PASSWORD_CHANGED, actor=current_user, request=request)
    db.commit()
    db.refresh(current_user)
    logger.info("User %s changed their password", current_user.id)

    return _token_response(current_user)
