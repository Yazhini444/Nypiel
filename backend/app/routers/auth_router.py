from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=schemas.Token)
def signup(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if db.query(models.User).filter(func.lower(models.User.email) == email).first():
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    user = models.User(
        email=email,
        name=payload.name,
        hashed_password=auth.hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = auth.create_access_token({"sub": str(user.id)})
    return schemas.Token(access_token=token, user=schemas.UserOut.model_validate(user))


@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.query(models.User).filter(func.lower(models.User.email) == email).first()
    if not user or not auth.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password.")

    token = auth.create_access_token({"sub": str(user.id)})
    return schemas.Token(access_token=token, user=schemas.UserOut.model_validate(user))


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user
