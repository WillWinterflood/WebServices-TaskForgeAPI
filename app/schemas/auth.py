from pydantic import BaseModel


class UserRegister(BaseModel):
    email: str
    full_name: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserRead(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
