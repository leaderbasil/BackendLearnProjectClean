from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from models.blog import Blog 

class BlogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, blog_id: int) -> Blog | None:
        result = await self.db.execute(select(Blog).where(Blog.id == blog_id))
        return result.scalar_one_or_none()

    async def get_page(self, page: int, size: int) -> tuple[list[Blog], int]:
        total_res = await self.db.execute(select(func.count(Blog.id)))
        total = total_res.scalar()
        items_res = await self.db.execute(
            select(Blog).order_by(Blog.id).offset((page - 1) * size).limit(size)
        )
        items = items_res.scalars().all()
        return items, total

    async def create(self, title: str, content: str, owner_id: int, file_url: Optional[str] = None) -> Blog:
        blog = Blog(title=title, content=content, owner_id=owner_id, file_url=file_url)
        self.db.add(blog)
        await self.db.flush()
        await self.db.refresh(blog)
        return blog

    async def update(self, blog: Blog, title: str, content: str, file_url: Optional[str] = None) -> Blog:
        blog.title = title
        blog.content = content
        blog.file_url = file_url
        await self.db.flush()
        await self.db.refresh(blog)
        return blog

    async def delete(self, blog: Blog) -> None:
        await self.db.delete(blog)
        await self.db.flush()