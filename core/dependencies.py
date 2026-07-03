import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from jose import JWTError

from .database import AsyncSessionLocal
from .auth import decode_access_token
from models.user import User  

logger = logging.getLogger("blog_api")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            async with session.begin():
                yield session
        except SQLAlchemyError:
            logger.error("DB transaction failed, rolled back.")
            raise
        finally:
            await session.close()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = decode_access_token(token)
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise credentials_exception
    return user

def get_blog_repository(db: AsyncSession = Depends(get_db)):
    from repositories.blog_repository import BlogRepository  
    return BlogRepository(db)

def get_blog_service(repository=Depends(get_blog_repository)):
    from modules.blog.services.blog_service import BlogService   
    return BlogService(repository)
    
def get_user_repository(db: AsyncSession = Depends(get_db)):
    from repositories.user_repository import UserRepository
    return UserRepository(db)

async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """تتحقق من أن المستخدم الحالي هو مدير (Superuser)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user

async def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """تتحقق من أن المستخدم قام بتأكيد بريده الإلكتروني"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email first."
        )
    return current_user

async def get_user_service(
    user_repo = Depends(get_user_repository), 
    db: AsyncSession = Depends(get_db)
):
    from repositories.token_repository import TokenRepository
    from modules.auth.services.auth_service import AuthService 
    token_repo = TokenRepository(db)
    return AuthService(user_repo, token_repo)