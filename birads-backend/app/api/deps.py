"""Shared FastAPI dependencies (auth, current user, role checks)."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import ROLE_ADMIN, User

bearer_scheme = HTTPBearer(auto_error=True)

PASSWORD_CHANGE_REQUIRED = "password_change_required"


def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the bearer token to an active user.

    Only the auth endpoints depend on this directly; everything else uses
    `get_current_user`, which also enforces the forced password change.
    """
    payload = decode_access_token(credentials.credentials)
    try:
        user = db.get(User, int(payload["sub"]))
    except (TypeError, ValueError):
        user = None
    # A stale token_version means the password changed or an admin reset it.
    if (
        user is None
        or not user.is_active
        or payload.get("tv") != user.token_version
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_user(user: User = Depends(get_authenticated_user)) -> User:
    if user.must_change_password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=PASSWORD_CHANGE_REQUIRED
        )
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required."
        )
    return user
