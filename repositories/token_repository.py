from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, timezone
from models.token import PasswordResetToken, EmailVerificationToken

class TokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_reset_token(self, user_id: int, token: str, expires_at: datetime) -> PasswordResetToken:
        """إنشاء رمز إعادة تعيين في قاعدة البيانات"""
        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        self.db.add(reset_token)
        await self.db.flush()
        await self.db.refresh(reset_token)
        return reset_token

    async def get_reset_token(self, token: str) -> PasswordResetToken | None:
        """البحث عن رمز إعادة تعيين"""
        result = await self.db.execute(
            select(PasswordResetToken).where(PasswordResetToken.token == token)
        )
        return result.scalar_one_or_none()

    async def delete_reset_token(self, token: str) -> None:
        """حذف الرمز بعد استخدامه"""
        await self.db.execute(
            delete(PasswordResetToken).where(PasswordResetToken.token == token)
        )
        await self.db.flush()

    async def delete_expired_reset_tokens(self, user_id: int) -> None:
        """حذف جميع الرموز منتهية الصلاحية لمستخدم معين (للتنظيف)"""
        await self.db.execute(
            delete(PasswordResetToken)
            .where(PasswordResetToken.user_id == user_id)
            .where(PasswordResetToken.expires_at < datetime.now(timezone.utc))
        )
        await self.db.flush()

    # ===== التحقق من البريد الإلكتروني (يمكنك نسخ نفس النمط لـ EmailVerificationToken) =====