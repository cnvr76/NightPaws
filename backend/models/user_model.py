from config.database import Base
from sqlalchemy import Column, Text, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid())
    username = Column(Text)
    avatar_url = Column(Text),
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    work_email = Column(Text)
    gmail_refresh_token = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    applications = relationship("Application", back_populates="user")