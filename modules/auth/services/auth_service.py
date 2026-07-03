from datetime import datetime, timezone
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

from core.auth import hash_password, verify_password, create_access_token, create_reset_token
from core.exception import (
    ConflictException,
    UnauthorizedException,
    NotFoundException,
    ValidationException,
)
from repositories.user_repository import UserRepository
from repositories.token_repository import TokenRepository
from modules.auth.schemas import UserCreate, Token, ChangePassword, ForgotPassword, ResetPassword


class AuthService:
    def __init__(self, user_repo: UserRepository, token_repo: TokenRepository):
        self.user_repo = user_repo
        self.token_repo = token_repo
    #create new user
    async def register(self, user_in: UserCreate):
        # التحقق من وجود البريد
        existing = await self.user_repo.get_by_email(user_in.email)
        if existing:
            raise ConflictException("Email already registered")

        # تشفير كلمة المرور
        hashed = hash_password(user_in.password)
        try:
            user = await self.user_repo.create(user_in.email, hashed)
            return user
        except SQLAlchemyError as e:
            raise ValidationException(f"Database error: {str(e)}")

    # ===== 2. تسجيل الدخول =====
    async def login(self, email: str, password: str) -> Token:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid credentials")

        token = create_access_token(str(user.id))
        return Token(access_token=token)

    # ===== 3. تغيير كلمة المرور (أثناء تسجيل الدخول) =====
    async def change_password(self, user_id: int, data: ChangePassword) -> bool:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User")

        if not verify_password(data.current_password, user.hashed_password):
            raise ValidationException("Current password is incorrect")

        new_hashed = hash_password(data.new_password)
        await self.user_repo.update_password(user_id, new_hashed)
        return True

    # ===== 4. طلب إعادة تعيين كلمة المرور =====
    async def request_password_reset(self, data: ForgotPassword) -> str:
        """إنشاء رمز إعادة تعيين وإرجاعه (بدلاً من إرسال بريد إلكتروني)"""
        user = await self.user_repo.get_by_email(data.email)
        if not user:
            # لأمان، لا نخبر إذا كان البريد موجوداً أم لا (نمنع هجمات Enumeration)
            return "If this email exists, a reset token has been sent."

        # حذف الرموز القديمة
        await self.token_repo.delete_expired_reset_tokens(user.id)

        # إنشاء رمز جديد
        token, expires_at = create_reset_token(user.id)
        await self.token_repo.create_reset_token(user.id, token, expires_at)

        # 🔥 هنا يجب إرسال البريد الإلكتروني، لكننا نعيد الرمز للتجربة.
        return f"Reset token for {user.email}: {token}"

    # ===== 5. إعادة تعيين كلمة المرور (باستخدام الرمز) =====
    async def reset_password(self, data: ResetPassword) -> bool:
        token_record = await self.token_repo.get_reset_token(data.token)
        if not token_record:
            raise ValidationException("Invalid or expired token")

        if token_record.expires_at < datetime.now(timezone.utc):
            raise ValidationException("Token has expired")

        new_hashed = hash_password(data.new_password)
        await self.user_repo.update_password(token_record.user_id, new_hashed)
        await self.token_repo.delete_reset_token(data.token)
        return True