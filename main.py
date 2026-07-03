# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import time
from core.api import api_router
from core.database import engine, Base
from core.logging_config import logger
from core.exception import AppException

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
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.bind(
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration=f"{process_time:.3f}s"
    ).info("")
    return response

# ===== 🔥 معالج الأخطاء المركزي (يستمع لاستثناءات AppException) =====
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    logger.warning(f"AppException: {exc.error_code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        }
    )

# ===== معالجات الأخطاء الأخرى =====
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"⚠️ Validation error on {request.url.path}")
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

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(api_router)