from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.comment import Comment

class CommentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, comment_id: int) -> Comment | None:
        result = await self.db.execute(select(Comment).where(Comment.id == comment_id))
        return result.scalar_one_or_none()

    async def get_by_post_id(self, post_id: int, page: int, size: int) -> tuple[list[Comment], int]:
        total = await self.db.scalar(select(func.count(Comment.id)).where(Comment.post_id == post_id))
        items = await self.db.execute(
            select(Comment)
            .where(Comment.post_id == post_id)
            .order_by(Comment.id)
            .offset((page - 1) * size)
            .limit(size)
        )
        return items.scalars().all(), total

    async def create(self, content: str, post_id: int, user_id: int) -> Comment:
        comment = Comment(content=content, post_id=post_id, user_id=user_id)
        self.db.add(comment)
        await self.db.flush()
        await self.db.refresh(comment)
        return comment

    async def update(self, comment: Comment, content: str) -> Comment:
        comment.content = content
        await self.db.flush()
        await self.db.refresh(comment)
        return comment

    async def delete(self, comment: Comment) -> None:
        await self.db.delete(comment)
        await self.db.flush()