from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse, UserLogin, UserRead, UserRegister

router = APIRouter(prefix="/auth", tags=["2. Authentication Setup"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a user",
    description="Step 1 for protected features. Create an account before logging in and using the protected recipe write routes.",
)
def register_user(data: UserRegister, db=Depends(get_db)):
    email = data.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    if "@" not in email:
        raise HTTPException(status_code=400, detail="Email is invalid")

    full_name = data.full_name.strip()
    if not full_name:
        raise HTTPException(status_code=400, detail="Full name is required")

    if len(data.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")

    user = User(
        email=email,
        full_name=full_name,
        hashed_password=hash_password(data.password),
        is_active=True,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in and get a bearer token",
    description="Step 2 for protected features. Use the returned access_token with the Authorize button before creating, updating, or deleting your own recipes.",
)
def login_user(data: UserLogin, db=Depends(get_db)):
    email = data.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the current authenticated user",
    description="Step 3 for protected features. Call this after authorizing to confirm which account is currently logged in.",
)
def read_me(current_user=Depends(get_current_user)):
    return current_user
