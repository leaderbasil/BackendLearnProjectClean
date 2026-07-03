import logging
from typing import Optional
from fastapi import UploadFile, status
from sqlalchemy.exc import SQLAlchemyError

from core.imagekit_upload import imagekit_uploader
from core.exception import (
    NotFoundException,
    PermissionDeniedException,
    ValidationException,
)
from repositories.blog_repository import BlogRepository
from models.user import User

logger = logging.getLogger(__name__)

class BlogService:
    def __init__(self, repository: BlogRepository):
        self.repository = repository

    async def list_blogs(self, page: int, size: int) -> dict:
        items, total = await self.repository.get_page(page, size)
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
        }

    async def get_blog(self, blog_id: int):
        blog = await self.repository.get_by_id(blog_id)
        if not blog:
            raise NotFoundException("Blog")
        return blog

    async def _upload_image(self, file: UploadFile) -> str:
        """رفع الصورة إلى ImageKit"""
        return await imagekit_uploader.upload(file=file, folder="/blogs")

    async def create_blog(
        self,
        title: str,
        content: str,
        file: Optional[UploadFile],
        current_user: User
    ):
        file_url = None
        try:
            if file and file.filename:
                logger.info(f"Uploading file: {file.filename}")
                file_url = await self._upload_image(file)
                logger.info(f"File uploaded: {file_url}")

            blog = await self.repository.create(
                title=title,
                content=content,
                owner_id=current_user.id,
                file_url=file_url
            )
            return blog

        except Exception as e:
            raise ValidationException(f"Failed to create blog: {str(e)}")

    async def update_blog(
        self,
        blog_id: int,
        title: str,
        content: str,
        file: Optional[UploadFile],
        current_user: User
    ):
        blog = await self.get_blog(blog_id)

        if blog.owner_id != current_user.id:
            raise PermissionDeniedException("Not enough permissions to update this blog")

        file_url = blog.file_url
        try:
            if file and file.filename:
                file_url = await self._upload_image(file)

            return await self.repository.update(
                blog,
                title=title,
                content=content,
                file_url=file_url
            )

        except Exception as e:
            raise ValidationException(f"Failed to update blog: {str(e)}")

    async def delete_blog(self, blog_id: int, current_user: User):
        blog = await self.get_blog(blog_id)

        if blog.owner_id != current_user.id:
            raise PermissionDeniedException("Not enough permissions to delete this blog")

        await self.repository.delete(blog)