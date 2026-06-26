# core/logging_config.py
from loguru import logger
import sys
import logging

# ========== قتل سجلات SQLAlchemy وكل المكتبات المزعجة ==========
for name in [
    "sqlalchemy",
    "sqlalchemy.engine",
    "sqlalchemy.pool",
    "sqlalchemy.orm",
    "sqlalchemy.dialects",
    "sqlalchemy.sql",
    "uvicorn",
    "uvicorn.access",
    "uvicorn.error",
    "watchfiles",
    "httpcore",
    "httpx",
]:
    logging.getLogger(name).setLevel(logging.ERROR)

# ========== ألوان مخصصة للعرض البشري ==========
COLORS = {
    "GET": "\033[95m",      # بنفسجي
    "POST": "\033[94m",     # أزرق
    "PUT": "\033[93m",      # أصفر
    "DELETE": "\033[91m",   # أحمر
    "PATCH": "\033[96m",    # سماوي
    "2xx": "\033[92m",      # أخضر
    "3xx": "\033[96m",      # سماوي
    "4xx": "\033[93m",      # أصفر
    "5xx": "\033[91m",      # أحمر
    "RESET": "\033[0m",
}

def get_status_color(status_code: int) -> str:
    if 200 <= status_code < 300:
        return COLORS["2xx"]
    elif 300 <= status_code < 400:
        return COLORS["3xx"]
    elif 400 <= status_code < 500:
        return COLORS["4xx"]
    return COLORS["5xx"]

def format_log(record: dict) -> str:
    """
    تنسيق السجلات بحيث تكون:
    - مقروءة للبشر (ألوان)
    - مقروءة للذكاء الاصطناعي (فصل الأعمدة بـ '|')
    - تحتوي على: الوقت | المدة | الطريقة | المسار | الحالة
    """
    method = record["extra"].get("method", "")
    status = record["extra"].get("status", "")
    duration = record["extra"].get("duration", "")
    path = record["message"]
    level = record["level"].name

    # ألوان الطريقة
    method_color = COLORS.get(method, COLORS["RESET"])
    method_colored = f"{method_color}{method}{COLORS['RESET']}"

    # لون الحالة
    if status:
        status_color = get_status_color(int(status))
        status_colored = f"{status_color}{status}{COLORS['RESET']}"
    else:
        status_colored = status

    # لون المستوى (للتمييز)
    level_colors = {
        "INFO": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "SUCCESS": "\033[92m",
    }
    level_color = level_colors.get(level, COLORS["RESET"])
    level_colored = f"{level_color}{level}{COLORS['RESET']}"

    # التنسيق النهائي (مناسب للبشر والذكاء الاصطناعي)
    time_part = f"<green>{record['time']:HH:mm:ss}</green>"
    duration_part = f"[{duration}]" if duration else ""

    return f"{time_part} | {level_colored} | {duration_part} {method_colored} {path} → {status_colored}"

def setup_logging():
    logger.remove()
    
    # معالج للـ console مع ألوان
    logger.add(
        sys.stdout,
        format=format_log,
        level="INFO",
        colorize=True
    )
    
    # معالج للملف (بدون ألوان، مناسب للذكاء الاصطناعي)
    logger.add(
        "logs/app.log",
        rotation="100 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="DEBUG"
    )
    
    return logger

# تهيئة الـ logger فوراً
logger = setup_logging()