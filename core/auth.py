import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt
from .config import settings
import secrets
from datetime import datetime, timedelta, timezone 
def generate_random_token() -> str:
    """إنشاء رمز عشوائي طويل وآمن"""
    return secrets.token_urlsafe(32)

def create_reset_token(user_id: int) -> tuple[str, datetime]:
    """إنشاء رمز إعادة تعيين مع وقت انتهاء (ساعة واحدة)"""
    token = generate_random_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    return token, expires_at

def _truncate_password(password: str) -> bytes:
    """تقطيع كلمة المرور إلى 72 بايت كحد أقصى (لـ bcrypt)"""
    return password.encode('utf-8')[:72]

def hash_password(password: str) -> str:
    truncated = _truncate_password(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(truncated, salt)
    return hashed.decode('utf-8')  

def verify_password(plain_password: str, hashed_password: str) -> bool:
    truncated = _truncate_password(plain_password)
    return bcrypt.checkpw(truncated, hashed_password.encode('utf-8'))

def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> str:
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    subject: str | None = payload.get("sub")
    if subject is None:
        raise ValueError("Token missing subject")
    return subject