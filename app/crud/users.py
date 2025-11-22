from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate, UserUpdate
from typing import Optional

# ------------------------------
# Get user by email
# ------------------------------
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

# ------------------------------
# Get user by id
# ------------------------------
def get_user(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.user_id == user_id).first()

# ------------------------------
# Create user
# ------------------------------
def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=user.password,  # hash before using in production!
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ------------------------------
# Update user
# ------------------------------
def update_user(db: Session, db_user: User, updates: UserUpdate) -> User:
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user

# ------------------------------
# Delete user
# ------------------------------
def delete_user(db: Session, db_user: User):
    db.delete(db_user)
    db.commit()
