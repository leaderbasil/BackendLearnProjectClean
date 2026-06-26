from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BlogBase(BaseModel):
    title: str
    content: str

class BlogCreate(BlogBase):
    """للتحقق فقط - لا يستخدم مع رفع الملفات"""
    pass

class BlogOut(BlogBase):
    id: int
    owner_id: int
    file_url: Optional[str] = None  
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PaginatedBlogs(BaseModel):
    items: list[BlogOut]
    total: int
    page: int
    size: int