from fastapi import APIRouter, Depends, Query, Response, status, Form, File, UploadFile
from modules.blog.schemas import BlogOut, PaginatedBlogs, BlogCreate
from models.blog import User
from core.dependencies import get_blog_service, get_current_user  

router = APIRouter(prefix="/blog", tags=["blog"])

@router.get("", response_model=PaginatedBlogs)
async def get_blogs(
    service=Depends(get_blog_service),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    return await service.list_blogs(page, size)

@router.get("/{blog_id}", response_model=BlogOut)
async def get_blog(blog_id: int, service=Depends(get_blog_service)):
    return await service.get_blog(blog_id)

@router.post("", response_model=BlogOut, status_code=status.HTTP_201_CREATED)
async def create_blog(
    title: str = Form(...),                    
    content: str = Form(...),                  
    file: UploadFile = File(None),             
    service=Depends(get_blog_service),
    current_user: User = Depends(get_current_user),
):
    return await service.create_blog(title, content, file, current_user)

@router.put("/{blog_id}", response_model=BlogOut)
async def update_blog(
    blog_id: int,
    title: str = Form(...),
    content: str = Form(...),
    file: UploadFile = File(None),
    service=Depends(get_blog_service),
    current_user: User = Depends(get_current_user),
):
    return await service.update_blog(blog_id, title, content, file, current_user)

@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog(
    blog_id: int,
    service=Depends(get_blog_service),
    current_user: User = Depends(get_current_user),
):
    await service.delete_blog(blog_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)