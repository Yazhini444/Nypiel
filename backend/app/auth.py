import os
import datetime
import bcrypt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from . import models
from .database import get_db


# In production, set NYPIEL_SECRET_KEY as a real env var / secret
SECRET_KEY = os.getenv("NYPIEL_SECRET_KEY", "dev-only-change-me")

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week


# Bearer token authentication
security = HTTPBearer()


# Hash password
def hash_password(password: str) -> str:
    pw = password.encode("utf-8")[:72]

    return bcrypt.hashpw(
        pw,
        bcrypt.gensalt()
    ).decode("utf-8")


# Verify password
def verify_password(plain: str, hashed: str) -> bool:
    pw = plain.encode("utf-8")[:72]

    return bcrypt.checkpw(
        pw,
        hashed.encode("utf-8")
    )


# Create JWT access token
def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# Get currently authenticated user
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:

    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    # Verify JWT token
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        print(f"[AUTH] JWT decoded successfully. sub={user_id}")

        if user_id is None:
            print("[AUTH] JWT has no sub field")
            raise credentials_exception

    except JWTError as e:
        print(f"[AUTH] JWT decode FAILED: {e}")
        raise credentials_exception

    # Find user in database
    try:
        user = (
            db.query(models.User)
            .filter(models.User.id == int(user_id))
            .first()
        )
    except Exception as e:
        print(f"[AUTH] Database lookup FAILED: {e}")
        raise credentials_exception

    if user is None:
        print(f"[AUTH] USER NOT FOUND: id={user_id}")
        raise credentials_exception

    print(
        f"[AUTH] User authenticated: "
        f"id={user.id}, email={user.email}"
    )

    return user