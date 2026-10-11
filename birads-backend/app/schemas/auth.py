from pydantic import BaseModel


class GoogleLoginRequest(BaseModel):
    id_token: str


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    picture: str
    role: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
