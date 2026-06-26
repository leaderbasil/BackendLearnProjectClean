from loguru import logger
import sys
import logging
from pathlib import Path

def setup_logging():
    # إزالة إعدادات لوجورو الافتراضية
    logger.remove()

    # ===== 1. قتل رسائل SQLAlchemy نهائياً =====
    for name in ["sqlalchemy", "sqlalchemy.engine", "sqlalchemy.pool", "sqlalchemy.orm"]:
        logging.getLogger(name).setLevel(logging.ERROR)

    # ===== 2. تعريف الأشكال (Formats) =====
    
    # شكل مخصص لطلبات HTTP (الاحترافي)
    request_format = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>[{extra[duration]:>7}]</cyan> "
        "<level>{extra[method]: <7}</level> "
        "<b>{extra[path]:<30}</b> → "
        "<level>{extra[status]}</level>"
    )

    # شكل مخصص للرسائل العادية (بدون متغيرات مفقودة)
    standard_format = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    )

    # ===== 3. فلاتر لفصل أنواع السجلات =====
    
    # فلتر: يعرض فقط سجلات الطلبات (التي تحتوي على method)
    def is_request(record):
        return bool(record["extra"].get("method"))

    # فلتر: يعرض كل شيء آخر (أخطاء، معلومات عادية)
    def is_standard(record):
        return not is_request(record)

    # ===== 4. إضافة الهاندلرز (المنافذ) =====

    # منفذ الطباعة للطلبات
    logger.add(
        sys.stdout,
        format=request_format,
        filter=is_request,
        level="INFO",
        colorize=True
    )

    # منفذ الطباعة للرسائل العادية والأخطاء
    logger.add(
        sys.stdout,
        format=standard_format,
        filter=is_standard,
        level="INFO",
        colorize=True
    )

    # منفذ حفظ الأخطاء في ملف (للمراجعة لاحقاً)
    logger.add(
        Path("logs/errors.log"),
        rotation="10 MB",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )

setup_logging()