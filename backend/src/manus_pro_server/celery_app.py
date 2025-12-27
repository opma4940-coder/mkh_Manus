# ═══════════════════════════════════════════════════════════════════════════════
# تكوين Celery لنظام mkh_Manus
# يوفر نظام مهام موزع مع دعم retries و scheduling
# التاريخ: ديسمبر 2025
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations
import os
from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue

# ═══ تكوين Celery ═══
celery_app = Celery(
    "mkh_manus",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
    include=[
        "manus_pro_server.tasks",
    ]
)

# ═══ إعدادات عامة ═══
celery_app.conf.update(
    # التسلسل
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # النتائج
    result_expires=3600 * 24 * 7,  # أسبوع واحد
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
    },
    
    # إعادة المحاولة
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,  # ثانية
    task_max_retries=3,
    
    # الأداء
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # المراقبة
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # الأمان
    task_always_eager=False,  # False في الإنتاج
    task_eager_propagates=True,
    
    # Queues
    task_default_queue="default",
    task_default_exchange="tasks",
    task_default_exchange_type="direct",
    task_default_routing_key="default",
)

# ═══ تعريف Queues ═══
celery_app.conf.task_queues = (
    Queue("default", Exchange("tasks"), routing_key="default"),
    Queue("high_priority", Exchange("tasks"), routing_key="high"),
    Queue("low_priority", Exchange("tasks"), routing_key="low"),
    Queue("connectors", Exchange("tasks"), routing_key="connectors"),
    Queue("openmanus", Exchange("tasks"), routing_key="openmanus"),
)

# ═══ Routing ═══
celery_app.conf.task_routes = {
    "manus_pro_server.tasks.execute_openmanus_task": {
        "queue": "openmanus",
        "routing_key": "openmanus",
    },
    "manus_pro_server.tasks.connector_*": {
        "queue": "connectors",
        "routing_key": "connectors",
    },
    "manus_pro_server.tasks.cleanup_*": {
        "queue": "low_priority",
        "routing_key": "low",
    },
}

# ═══ Scheduled Tasks (Beat) ═══
celery_app.conf.beat_schedule = {
    # تنظيف المهام القديمة كل يوم في منتصف الليل
    "cleanup-old-tasks": {
        "task": "manus_pro_server.tasks.cleanup_old_tasks",
        "schedule": crontab(hour=0, minute=0),
        "options": {"queue": "low_priority"},
    },
    
    # تنظيف المرفقات المنتهية كل ساعة
    "cleanup-expired-attachments": {
        "task": "manus_pro_server.tasks.cleanup_expired_attachments",
        "schedule": crontab(minute=0),
        "options": {"queue": "low_priority"},
    },
    
    
    "refresh-connector-tokens": {
        "task": "manus_pro_server.tasks.refresh_connector_tokens",
        "schedule": crontab(minute="*/5"),
        "options": {"queue": "connectors"},
    },
    
    # إنشاء تقرير صحة النظام كل ساعة
    "system-health-check": {
        "task": "manus_pro_server.tasks.system_health_check",
        "schedule": crontab(minute=30),
        "options": {"queue": "default"},
    },
}

# ═══ Error Handling ═══
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def task_with_retry(self, *args, **kwargs):
    """مهمة مع إعادة محاولة تلقائية"""
    try:
        # تنفيذ المهمة
        pass
    except Exception as exc:
        # إعادة المحاولة مع backoff exponential
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

# ═══ Signals ═══
from celery.signals import (
    task_prerun, task_postrun, task_failure, 
    task_retry, task_revoked, worker_ready
)

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """يتم استدعاؤه قبل بدء المهمة"""
    from .logging_config import get_logger
    logger = get_logger(__name__)
    logger.info(f"Task {task.name} [{task_id}] started")

@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, **extra):
    """يتم استدعاؤه بعد انتهاء المهمة"""
    from .logging_config import get_logger
    logger = get_logger(__name__)
    logger.info(f"Task {task.name} [{task_id}] completed")

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **extra):
    """يتم استدعاؤه عند فشل المهمة"""
    from .logging_config import get_logger
    logger = get_logger(__name__)
    logger.error(f"Task {sender.name} [{task_id}] failed: {exception}")
    
    # إرسال إلى Sentry إذا كان متاحاً
    try:
        import sentry_sdk
        sentry_sdk.capture_exception(exception)
    except ImportError:
        pass

@task_retry.connect
def task_retry_handler(sender=None, task_id=None, reason=None, einfo=None, **extra):
    """يتم استدعاؤه عند إعادة محاولة المهمة"""
    from .logging_config import get_logger
    logger = get_logger(__name__)
    logger.warning(f"Task {sender.name} [{task_id}] retrying: {reason}")

@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """يتم استدعاؤه عند جاهزية Worker"""
    from .logging_config import get_logger
    logger = get_logger(__name__)
    logger.info("Celery worker is ready and waiting for tasks")

if __name__ == "__main__":
    celery_app.start()
