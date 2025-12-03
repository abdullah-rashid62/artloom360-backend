from sqlalchemy.orm import Session
from typing import Optional
from pwdlib import PasswordHash
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate


# Password hashing instance
password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.user_id == user_id).first()

def create_user(db: Session, user: UserCreate) -> User:
    hashed = hash_password(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: User, updates: UserUpdate) -> User:
    data = updates.dict(exclude_unset=True)
    if "password" in data:
        data["password_hash"] = hash_password(data.pop("password"))
    for k, v in data.items():
        setattr(db_user, k, v)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, db_user: User):
    db.delete(db_user)
    db.commit()
