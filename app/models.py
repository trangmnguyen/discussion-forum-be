# pylint: disable=not-callable
from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)

class Discussion(Base):
    __tablename__ = "discussions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    body = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    body = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))
    discussion_id = Column(Integer, ForeignKey("discussions.id"))
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
