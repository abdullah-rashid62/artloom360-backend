from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.schemas.users import UserCreate, UserLogin, UserResponse, TokenResponse
from app.crud import users as crud_users
from app.core.database import SessionLocal
from app.utils.auth import create_access_token, get_current_active_user, get_db, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["Users"])

@router.post("/signup", response_model=TokenResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = crud_users.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = crud_users.create_user(db, user)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.user_id},  
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer", "user": new_user}

@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = crud_users.get_user_by_email(db, user.email)
    if not db_user or not crud_users.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": db_user.user_id}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "user": db_user}

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user = Depends(get_current_active_user)):
    return current_user
