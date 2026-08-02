from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from orchx_api.core.auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from orchx_api.core.database import get_db
from orchx_api.models import AuditLog, User
from orchx_api.schemas import Token, UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new workspace user."""
    result = await db.execute(select(User).filter(User.email == user_in.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        is_active=True,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    audit_log = AuditLog(
        user_id=db_user.id,
        action="USER_REGISTER",
        details={"email": db_user.email},
    )
    db.add(audit_log)
    await db.commit()

    return db_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Retrive JWT Access Token."""
    result = await db.execute(select(User).filter(User.email == form_data.username))
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    audit_log = AuditLog(
        user_id=user.id,
        action="USER_LOGIN",
        details={"email": user.email},
    )
    db.add(audit_log)
    await db.commit()

    return {
        "access_token": create_access_token(user.email),
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
async def read_user_me(current_user: User = Depends(get_current_user)):
    """Retrieve logged-in user."""
    return current_user
