from core.exception import NotFoundException, PermissionDeniedException
from repositories.comment_repository import CommentRepository
from modules.comments.schemas import CommentCreate, CommentUpdate
from models.user import User

class CommentService:
    def __init__(self, repo: CommentRepository):
        self.repo = repo

    async def list_comments(self, post_id: int, page: int, size: int):
        items, total = await self.repo.get_by_post_id(post_id, page, size)
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
        }

    async def get_comment(self, comment_id: int):
        comment = await self.repo.get_by_id(comment_id)
        if not comment:
            raise NotFoundException("Comment")
        return comment

    async def create_comment(self, data: CommentCreate, current_user: User):
        return await self.repo.create(data.content, data.post_id, current_user.id)

    async def update_comment(self, comment_id: int, data: CommentUpdate, current_user: User):
        comment = await self.get_comment(comment_id)
        if comment.user_id != current_user.id:
            raise PermissionDeniedException("Not enough permissions to update this comment")
        return await self.repo.update(comment, data.content)

    async def delete_comment(self, comment_id: int, current_user: User):
        comment = await self.get_comment(comment_id)
        if comment.user_id != current_user.id:
            raise PermissionDeniedException("Not enough permissions to delete this comment")
        await self.repo.delete(comment)