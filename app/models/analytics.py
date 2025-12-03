import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Index
from app.core.database import Base

def gen_uuid():
    return str(uuid.uuid4())

class ViewEvent(Base):
    __tablename__ = "views"

    view_id = Column(String(36), primary_key=True, default=gen_uuid)
    target_type = Column(String(50), nullable=False)  # 'artwork' or 'exhibition'
    target_id = Column(String(36), nullable=False, index=True)
    session_id = Column(String(36), nullable=True, index=True)
    ip_hash = Column(String(128), nullable=True)  # store hashed IP (optional)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_views_target_type_id_created", "target_type", "target_id", "created_at"),
    )


class LikeEvent(Base):
    __tablename__ = "likes"

    like_id = Column(String(36), primary_key=True, default=gen_uuid)
    target_type = Column(String(50), nullable=False)
    target_id = Column(String(36), nullable=False, index=True)
    session_id = Column(String(36), nullable=True)
    ip_hash = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_likes_target_type_id_created", "target_type", "target_id", "created_at"),
    )


class WatchTimeEvent(Base):
    __tablename__ = "watch_time"

    watch_id = Column(String(36), primary_key=True, default=gen_uuid)
    target_type = Column(String(50), nullable=False)
    target_id = Column(String(36), nullable=False, index=True)
    session_id = Column(String(36), nullable=True)
    seconds_watched = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_watch_time_target_type_id_created", "target_type", "target_id", "created_at"),
    )


class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(String(36), primary_key=True, default=gen_uuid)
    target_type = Column(String(50), nullable=False)
    target_id = Column(String(36), nullable=False, index=True)
    session_id = Column(String(36), nullable=True)
    ip_hash = Column(String(128), nullable=True)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_reviews_target_type_id_created", "target_type", "target_id", "created_at"),
    )
