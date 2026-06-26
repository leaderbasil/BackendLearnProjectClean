from fastapi import HTTPException, status, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from core.images import imagekit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from repositories.blog_repository import BlogRepository
from models.blog import User
import tempfile
import os
from typing import Optional


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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Blog not found"
            )
        return blog

    async def _upload_to_imagekit(self, file: UploadFile) -> str:
        """دالة مساعدة لرفع الملف إلى ImageKit"""
        temp_file_path = None
        
        try:
            # تحديد امتداد الملف
            file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
            
            # إنشاء ملف مؤقت
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=file_extension
            )
            temp_file_path = temp_file.name
            
            # قراءة محتوى الملف وكتابته
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            
            # رفع الملف إلى ImageKit
            upload_response = imagekit.upload_file(
                file=open(temp_file_path, 'rb'),
                file_name=file.filename,
                options=UploadFileRequestOptions(
                    folder="/blogs",
                    use_unique_file_name=True
                )
            )
            
            # التحقق من نجاح الرفع
            if upload_response.response.http_status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"ImageKit upload failed: {upload_response.response.raw}"
                )
            
            return upload_response.url
            
        finally:
            # حذف الملف المؤقت دائماً
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    async def create_blog(
        self, 
        title: str, 
        content: str, 
        file: Optional[UploadFile], 
        current_user: User
    ):
        file_url = None
        
        try:
            # رفع الملف إذا تم إرساله
            if file and file.filename:
                file_url = await self._upload_to_imagekit(file)
            
            # حفظ في قاعدة البيانات
            blog = await self.repository.create(
                title=title,
                content=content,
                owner_id=current_user.id,
                file_url=file_url
            )
            return blog
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Database error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=str(e)
            )

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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Not enough permissions"
            )
        
        file_url = blog.file_url  # الاحتفاظ بالرابط القديم افتراضياً
        
        try:
            # رفع ملف جديد إذا تم إرساله
            if file and file.filename:
                file_url = await self._upload_to_imagekit(file)
            
            return await self.repository.update(
                blog, 
                title=title, 
                content=content, 
                file_url=file_url
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=str(e)
            )

    async def delete_blog(self, blog_id: int, current_user: User):
        blog = await self.get_blog(blog_id)
        
        if blog.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Not enough permissions"
            )
        
        await self.repository.delete(blog)