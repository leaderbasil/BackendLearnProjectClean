from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from core.auth import hash_password, verify_password, create_access_token
from repositories.user_repository import UserRepository
from modules.auth.schemas import UserCreate, Token

class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register(self, user_in: UserCreate):
        existing = await self.repository.get_by_email(user_in.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        hashed = hash_password(user_in.password)
        try:
            user = await self.repository.create(user_in.email, hashed)
            return user
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def login(self, email: str, password: str):
        user = await self.repository.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        token = create_access_token(str(user.id))
        return Token(access_token=token)

    async def change_password(self, user_id: int, data: ChangePassword) -> bool:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not verify_password(data.current_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        new_hashed = hash_password(data.new_password)
        await self.user_repo.update_password(user_id, new_hashed)
        return True

    async def request_password_reset(self, data: ForgotPassword) -> str:
        """إنشاء رمز إعادة تعيين وإرجاعه (بدلاً من إرسال بريد إلكتروني)"""
        user = await self.user_repo.get_by_email(data.email)
        if not user:
            return "If this email exists, a reset token has been sent."
        
        await self.token_repo.delete_expired_reset_tokens(user.id)
        token, expires_at = create_reset_token(user.id)
        await self.token_repo.create_reset_token(user.id, token, expires_at)
        
        return f"Reset token for {user.email}: {token}"

    async def reset_password(self, data: ResetPassword) -> bool:
        token_record = await self.token_repo.get_reset_token(data.token)
        if not token_record:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        
        if token_record.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Token has expired")
        
        new_hashed = hash_password(data.new_password)
        await self.user_repo.update_password(token_record.user_id, new_hashed)
        await self.token_repo.delete_reset_token(data.token)
        return True
