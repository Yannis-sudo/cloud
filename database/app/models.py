"""Database models."""

from sqlalchemy import Column, Integer, String
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

class User(Base):
    """User database model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)