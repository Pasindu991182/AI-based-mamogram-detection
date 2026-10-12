"""Write entries to the security audit trail."""
from fastapi import Request
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User

LOGIN_SUCCESS = "login_success"
LOGIN_FAILED = "login_failed"
ACCOUNT_LOCKED = "account_locked"
LOGOUT = "logout"
PASSWORD_CHANGED = "password_changed"
USER_CREATED = "user_created"
USER_UPDATED = "user_updated"
USER_DEACTIVATED = "user_deactivated"
USER_REACTIVATED = "user_reactivated"
PASSWORD_RESET = "password_reset"


def record(
    db: Session,
    action: str,
    *,
    actor: User | None = None,
    actor_email: str = "",
    target: str = "",
    request: Request | None = None,
) -> None:
    """Queue an audit row on the session; the caller commits."""
    ip = request.client.host if request is not None and request.client else ""
    db.add(
        AuditLog(
            actor_id=actor.id if actor else None,
            actor_email=(actor.email if actor else actor_email)[:320],
            action=action,
            target=target[:320],
            ip_address=ip[:64],
        )
    )
