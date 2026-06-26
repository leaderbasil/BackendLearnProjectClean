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