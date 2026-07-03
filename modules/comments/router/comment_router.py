from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user, get_db
from modules.comments.schemas import CommentCreate, CommentUpdate, CommentOut, PaginatedComments
from modules.comments.services.comment_services import CommentService
from repositories.comment_repository import CommentRepository
from models.user import User

router = APIRouter(prefix="/comments", tags=["comments"])

# ===== دوال التبعية =====
def get_comment_repository(db: AsyncSession = Depends(get_db)):
    return CommentRepository(db)

def get_comment_service(repo: CommentRepository = Depends(get_comment_repository)):
    return CommentService(repo)

# ===== نقاط النهاية =====

@router.get("/post/{post_id}", response_model=PaginatedComments)
async def list_comments(
    post_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    service: CommentService = Depends(get_comment_service)
):
    return await service.list_comments(post_id, page, size)

@router.get("/{comment_id}", response_model=CommentOut)
async def get_comment(
    comment_id: int,
    service: CommentService = Depends(get_comment_service)
):
    return await service.get_comment(comment_id)

@router.post("", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(
    data: CommentCreate,
    service: CommentService = Depends(get_comment_service),
    current_user: User = Depends(get_current_user)
):
    return await service.create_comment(data, current_user)

@router.put("/{comment_id}", response_model=CommentOut)
async def update_comment(
    comment_id: int,
    data: CommentUpdate,
    service: CommentService = Depends(get_comment_service),
    current_user: User = Depends(get_current_user)
):
    return await service.update_comment(comment_id, data, current_user)

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    service: CommentService = Depends(get_comment_service),
    current_user: User = Depends(get_current_user)
):
    await service.delete_comment(comment_id, current_user)
    return None