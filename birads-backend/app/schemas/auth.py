from datetime import datetime, timezone
from typing import Annotated, Literal, Optional

from pydantic import AfterValidator, BaseModel, Field, StringConstraints

Role = Literal["admin", "radiologist"]

# SQLite returns naive datetimes (stored as UTC); tag them so clients don't
# read them as local time. PostgreSQL values are already timezone-aware.
UtcDatetime = Annotated[
    datetime,
    AfterValidator(lambda d: d if d.tzinfo else d.replace(tzinfo=timezone.utc)),
]

# Normalised to lower-case so sign-in is case-insensitive. Deliberately loose:
# hospital intranet domains (e.g. name@radiology.local) must be accepted.
Email = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        to_lower=True,
        max_length=320,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    ),
]


class LoginRequest(BaseModel):
    email: Email
    password: str = Field(..., min_length=1, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=1, max_length=128)


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: str
    must_change_password: bool = False

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserOut


# --- Admin user management ------------------------------------------------
class AdminUserOut(UserOut):
    is_active: bool
    locked: bool = False
    last_login_at: Optional[UtcDatetime] = None
    case_count: int = 0


class AdminOverview(BaseModel):
    """Aggregate counts only — the admin role never sees patient records."""
    users_total: int
    users_active: int
    users_admin: int
    users_locked: int
    users_pending_password: int
    sessions_active: int
    failed_logins_24h: int
    cases_total: int
    cases_by_status: dict[str, int]


class AuditEntry(BaseModel):
    id: int
    created_at: UtcDatetime
    actor_email: str
    action: str
    target: str
    ip_address: str

    class Config:
        from_attributes = True


class AdminUserCreate(BaseModel):
    email: Email
    name: str = Field(..., min_length=1, max_length=255)
    role: Role = "radiologist"
    # Temporary password; the user is forced to replace it at first sign-in.
    password: str = Field(..., min_length=1, max_length=128)


class AdminUserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[Role] = None
    is_active: Optional[bool] = None


class AdminPasswordReset(BaseModel):
    password: str = Field(..., min_length=1, max_length=128)
