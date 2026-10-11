"""Google OAuth login → app JWT."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, verify_google_id_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import GoogleLoginRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/google", response_model=TokenResponse)
def login_with_google(body: GoogleLoginRequest, db: Session = Depends(get_db)):
    claims = verify_google_id_token(body.id_token)

    user = db.query(User).filter(User.google_sub == claims["sub"]).first()
    if user is None:
        user = User(
            google_sub=claims["sub"],
            email=claims["email"],
            name=claims["name"],
            picture=claims["picture"],
        )
        db.add(user)
    else:
        # Keep profile fields fresh on each login.
        user.email = claims["email"] or user.email
        user.name = claims["name"] or user.name
        user.picture = claims["picture"] or user.picture
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id), extra={"email": user.email})
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)
