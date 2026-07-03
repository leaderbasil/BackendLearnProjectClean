from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CommentCreate(BaseModel):
    content: str
    post_id: int

class CommentUpdate(BaseModel):
    content: str

class CommentOut(BaseModel):
    id: int
    content: str
    post_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PaginatedComments(BaseModel):
    items: list[CommentOut]
    total: int
    page: int
    size: int