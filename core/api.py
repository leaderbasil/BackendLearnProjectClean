# core/api.py
from fastapi import APIRouter
from typing import TypeVar, Generic, Optional, List
from pydantic import BaseModel

# ===== استيراد الراوترات من الموديولات =====
from modules.auth.router import router as auth_router
from modules.blog.router import router as blog_router
from modules.comments.router import router as comments_router

# ===== 1. تجميع الراوترات في راوتر رئيسي =====
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)      # /api/v1/auth/...
api_router.include_router(blog_router)      # /api/v1/blog/...
api_router.include_router(comments_router)  # /api/v1/comments/...

# ===== 2. (اختياري) توحيد شكل الردود =====
T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    """هيكل موحد للردود الناجحة"""
    success: bool = True
    data: T
    message: Optional[str] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """هيكل موحد للقوائم مع ترقيم الصفحات"""
    success: bool = True
    data: List[T]
    page: int
    size: int
    total: int
    total_pages: int

def success_response(data: T, message: Optional[str] = None) -> APIResponse[T]:
    """دالة مساعدة لإنشاء رد نجاح"""
    return APIResponse(data=data, message=message)

def paginated_response(
    items: List[T],
    total: int,
    page: int,
    size: int
) -> PaginatedResponse[T]:
    """دالة مساعدة لإنشاء رد مع ترقيم صفحات"""
    total_pages = (total + size - 1) // size
    return PaginatedResponse(
        data=items,
        page=page,
        size=size,
        total=total,
        total_pages=total_pages
    )