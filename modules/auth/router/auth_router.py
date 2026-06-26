from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import get_db
from repositories.user_repository import UserRepository
from modules.auth.services.auth_service import AuthService
from modules.auth.schemas import UserCreate, Token

router = APIRouter(prefix="/auth", tags=["auth"])

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_auth_service(repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(repo)

@router.post("/register")
async def register(user_in: UserCreate, service: AuthService = Depends(get_auth_service)):
    user = await service.register(user_in)
    return {"id": user.id, "email": user.email}

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    # OAuth2PasswordRequestForm يحوي username و password
    return await service.login(form_data.username, form_data.password)