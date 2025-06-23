from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str

class UserOut(BaseModel):
    id: int
    username: str
    class Config:
        orm_mode = True

class DiscussionCreate(BaseModel):
    title: str
    body: str

class DiscussionOut(BaseModel):
    id: int
    title: str
    body: str
    author_id: int
    created_at: datetime
    deleted: Optional[bool] = False
    deleted_at: Optional[datetime] = None
    class Config:
        orm_mode = True

class CommentCreate(BaseModel):
    body: str
    parent_id: Optional[int] = None

class CommentOut(BaseModel):
    id: int
    body: str
    author_id: int
    discussion_id: int
    parent_id: Optional[int]
    created_at: datetime
    deleted: Optional[bool] = False
    deleted_at: Optional[datetime] = None
    class Config:
        orm_mode = True