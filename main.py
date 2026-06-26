# main.py
import logging
# ===== قتل SQLAlchemy فوراً =====
logging.getLogger("sqlalchemy").setLevel(logging.ERROR)
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)
logging.getLogger("sqlalchemy.pool").setLevel(logging.ERROR)
logging.getLogger("sqlalchemy.orm").setLevel(logging.ERROR)

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import time

from modules.auth import router as auth_router
from core.database import engine, Base
from modules.blog.router import router as blog_router
from core.logging_config import logger

# ===== عداد الطلبات =====
request_counter = 0

# ===== حدث بدء وإيقاف التطبيق =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("🚀 Application startup complete.")
    yield
    await engine.dispose()
    logger.info("🛑 Application shutdown complete.")

app = FastAPI(title="Blog API", lifespan=lifespan)

# ===== Middleware لتسجيل الطلبات =====
@app.middleware("http")
async def log_requests(request: Request, call_next):
    global request_counter
    request_counter += 1

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # تسجيل الطلب مع البيانات المطلوبة
    logger.bind(
        method=request.method,
        status=response.status_code,
        duration=f"{process_time:.4f}s"
    ).info(request.url.path)

    # إضافة فاصل بعد كل طلب (باستثناء الأول)
    if request_counter > 1:
        # الفاصل = 60 علامة "="
        logger.bind(method="", status="", duration="").info("=" * 60)

    return response

# ===== معالجات الأخطاء =====
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"⚠️ Validation error on {request.url.path}")
    errors = []
    for error in exc.errors():
        err = {k: str(v) if isinstance(v, bytes) else v for k, v in error.items()}
        errors.append(err)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"💥 Unhandled error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

# ===== نقاط النهاية =====
@app.get("/")
async def root():
    return {"message": "Hello World"}

# ===== تسجيل الراوترات =====
app.include_router(auth_router)
app.include_router(blog_router)