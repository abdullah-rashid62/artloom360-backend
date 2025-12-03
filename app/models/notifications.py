import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

def gen_uuid():
    return str(uuid.uuid4())

class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(
        String(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    type = Column(String(50), nullable=False)           # 'order', 'review', 'like', 'system', etc.
    target_type = Column(String(50), nullable=True)     # 'order', 'artwork', 'exhibition', 'review', etc.
    target_id = Column(String(36), nullable=True)       # related entity id
    link_url = Column(Text, nullable=True)              # optional frontend route

    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", backref="notifications")

    __table_args__ = (
        Index("ix_notifications_user_read_created", "user_id", "is_read", "created_at"),
    )

    def __repr__(self):
        return f"<Notification {self.notification_id} {self.type}>"
