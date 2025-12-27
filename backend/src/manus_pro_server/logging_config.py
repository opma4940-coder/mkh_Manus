# إعداد التسجيل المنظم (Structured Logging) باستخدام structlog.
# يوفر تنسيق JSON لسهولة التحليل والمراقبة في بيئات الإنتاج.

import logging
import sys
import structlog
from structlog.processors import JSONRenderer

def configure_logging(log_level: str = "INFO"):
    """
    إعداد التسجيل المنظم (Structured Logging) للنظام.
    """
    # إعداد logging القياسي
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # إعداد structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            JSONRenderer(), # الإخراج بتنسيق JSON
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # إعداد loggers أخرى لاستخدام structlog
    for name in ["uvicorn", "uvicorn.access", "fastapi"]:
        logger = logging.getLogger(name)
        logger.handlers = [logging.StreamHandler(sys.stdout)]
        logger.propagate = False

# تهيئة التسجيل عند استيراد الملف
configure_logging()

# دالة مساعدة للحصول على logger
def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
