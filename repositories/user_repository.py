from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.blog import Blog
from models.user import User 
class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password, is_active=1)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def update_password(self, user_id: int, new_hashed_password: str) -> User:
        """تحديث كلمة مرور المستخدم"""
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        user.hashed_password = new_hashed_password
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_verification(self, user_id: int) -> User:
        """تحديث حالة التحقق من البريد إلى True"""
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        user.is_verified = True
        await self.db.flush()
        await self.db.refresh(user)
        return user