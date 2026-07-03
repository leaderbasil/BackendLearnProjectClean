from typing import Any, Optional

class AppException(Exception):
    """
    الاستثناء الأساسي للتطبيق.
    كل الأخطاء المخصصة ترث من هذا الكلاس لتوحيد شكل الرد.
    """
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "BAD_REQUEST",
        details: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(message)

# ===== أخطاء محددة (لتسهيل الاستخدام في الخدمات) =====

class NotFoundException(AppException):
    """404 - المورد غير موجود"""
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            message=f"{resource} not found",
            status_code=404,
            error_code="NOT_FOUND"
        )

class PermissionDeniedException(AppException):
    """403 - لا تملك الصلاحية"""
    def __init__(self, message: str = "Not enough permissions"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="PERMISSION_DENIED"
        )

class UnauthorizedException(AppException):
    """401 - غير مصرح (مشكلة في التوكن)"""
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED",
            details={"WWW-Authenticate": "Bearer"}
        )

class ConflictException(AppException):
    """409 - تضارب (مثل: البريد موجود مسبقاً)"""
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT"
        )

class ValidationException(AppException):
    """422 - فشل التحقق من صحة البيانات"""
    def __init__(self, message: str = "Validation error", details: Any = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details
        )