from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChangePassword(BaseModel):
    """لتغيير كلمة المرور أثناء تسجيل الدخول"""
    current_password: str
    new_password: str

class ForgotPassword(BaseModel):
    """لطلب إعادة تعيين كلمة المرور"""
    email: EmailStr

class ResetPassword(BaseModel):
    """لإعادة تعيين كلمة المرور باستخدام الرمز"""
    token: str
    new_password: str

class VerifyEmail(BaseModel):
    """لتأكيد البريد الإلكتروني"""
    token: str

class RequestVerifyEmail(BaseModel):
    """لطلب إرسال رمز تأكيد البريد"""
    email: EmailStr