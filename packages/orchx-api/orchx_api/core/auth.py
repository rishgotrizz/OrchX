import bcrypt
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from orchx_api.core.database import get_db
from orchx_api.models import User
from orchx_api.schemas import TokenPayload

import os
import logging
import secrets

env_raw = os.environ.get("ORCHX_ENV", "development")
ORCHX_ENV = env_raw.strip().lower() if env_raw and env_raw.strip() else "development"
SECRET_KEY = os.environ.get("ORCHX_JWT_SECRET")

if ORCHX_ENV == "production":
    if not SECRET_KEY or SECRET_KEY.strip() == "":
        raise ValueError("ORCHX_JWT_SECRET environment variable must be explicitly configured in production mode.")
else:
    # Development fallback
    if not SECRET_KEY or SECRET_KEY.strip() == "":
        # Generate an ephemeral process-local key
        SECRET_KEY = secrets.token_hex(32)
        logger = logging.getLogger("orchx_api.core.auth")
        logger.warning("ORCHX_JWT_SECRET not configured. Generated a process-local ephemeral JWT secret key for development.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).filter(User.email == token_data.sub))
    user = result.scalars().first()

    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user
