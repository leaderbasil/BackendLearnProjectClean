from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import get_db, get_current_superuser
from models import User
from repositories.user_repository import UserRepository
from modules.auth.services.auth_service import AuthService
from modules.auth.schemas import *
from core.dependencies import get_current_user, get_db, get_user_service

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


# ===== 1. تغيير كلمة المرور =====
@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    data: ChangePassword,
    current_user: User = Depends(get_current_user),
    service = Depends(get_user_service)
):
    """تغيير كلمة المرور للمستخدم الحالي (يتطلب تسجيل الدخول)"""
    result = await service.change_password(current_user.id, data)
    return {"message": "Password changed successfully"}

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    data: ForgotPassword,
    service = Depends(get_user_service)
):
    """طلب إعادة تعيين كلمة المرور (إرسال رمز للبريد الإلكتروني)"""
    message = await service.request_password_reset(data)
    return {"message": message}

@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    data: ResetPassword,
    service = Depends(get_user_service)
):
    """إعادة تعيين كلمة المرور باستخدام الرمز المستلم"""
    result = await service.reset_password(data)
    return {"message": "Password reset successfully"}

@router.get("/admin-only")
async def admin_only_route(
    current_user: User = Depends(get_current_superuser)  
):
    return {"message": f"Welcome Admin {current_user.email}!"}
