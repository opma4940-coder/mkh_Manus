# ═══════════════════════════════════════════════════════════════════════════════
# مهام Celery لنظام mkh_Manus
# يحتوي على جميع المهام الخلفية القابلة للتوزيع
# التاريخ: ديسمبر 2025
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from celery import Task
from .celery_app import celery_app
from .logging_config import get_logger

logger = get_logger(__name__)

# ═══ Base Task Class ═══
class CallbackTask(Task):
    """مهمة أساسية مع callbacks"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """يتم استدعاؤه عند نجاح المهمة"""
        logger.info(f"Task {self.name} [{task_id}] succeeded")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """يتم استدعاؤه عند فشل المهمة"""
        logger.error(f"Task {self.name} [{task_id}] failed: {exc}")
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """يتم استدعاؤه عند إعادة محاولة المهمة"""
        logger.warning(f"Task {self.name} [{task_id}] retrying: {exc}")

# ═══ Subtask Processing ═══
@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="manus_pro_server.tasks.process_subtask",
    max_retries=5,
)
def process_subtask(
    self,
    subtask_id: str,
    idempotency_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    معالجة مهمة فرعية مع إعادة محاولة تلقائية
    
    Args:
        subtask_id: معرف المهمة الفرعية
        idempotency_key: مفتاح التفرد لتجنب التكرار
    
    Returns:
        نتيجة المعالجة
    """
    try:
        logger.info(f"Processing subtask: {subtask_id} (idempotency_key: {idempotency_key})")
        
        # منطق معالجة المهمة الفرعية
        # يمكن إضافة المنطق الفعلي هنا
        
        return {
            "subtask_id": subtask_id,
            "status": "done",
            "idempotency_key": idempotency_key,
            "processed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Subtask processing failed: {subtask_id} - {exc}")
        
        # حساب وقت الانتظار قبل إعادة المحاولة (exponential backoff)
        countdown = min(60 * (2 ** self.request.retries), 3600)
        
        logger.info(f"Retrying subtask {subtask_id} in {countdown} seconds (attempt {self.request.retries + 1}/5)")
        
        raise self.retry(exc=exc, countdown=countdown)

# ═══ OpenManus Task Execution ═══
@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="manus_pro_server.tasks.execute_openmanus_task",
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def execute_openmanus_task(
    self,
    task_id: str,
    goal: str,
    project_path: str,
    available_api_keys: Dict[str, str],
    cycle_steps: int = 5,
    prior_messages: list = None
) -> Dict[str, Any]:
    """
    تنفيذ مهمة OpenManus
    
    Args:
        task_id: معرف المهمة
        goal: هدف المهمة
        project_path: مسار المشروع
        available_api_keys: مفاتيح API المتاحة
        cycle_steps: عدد خطوات الدورة
        prior_messages: الرسائل السابقة
    
    Returns:
        نتيجة التنفيذ
    """
    try:
        from .openmanus_bridge import run_openmanus_cycle
        from . import db
        
        logger.info(f"Starting OpenManus task execution: {task_id}")
        
        
        db.update_task_fields(task_id, status="running")
        db.add_event(task_id, "info", "task.started", "Task execution started via Celery")
        
        # تنفيذ الدورة
        result = asyncio.run(run_openmanus_cycle(
            task_id=task_id,
            available_api_keys=available_api_keys,
            goal=goal,
            project_path=project_path,
            cycle_steps=cycle_steps,
            prior_messages=prior_messages or []
        ))
        
        
        status = "completed" if result.finished else "running"
        db.update_task_fields(
            task_id,
            status=status,
            progress=1.0 if result.finished else 0.5,
            completed_at=datetime.utcnow().isoformat() if result.finished else None
        )
        
        db.add_event(
            task_id,
            "info",
            "task.completed" if result.finished else "task.progress",
            f"Cycle completed. Status: {status}"
        )
        
        logger.info(f"OpenManus task {task_id} execution completed: {status}")
        
        return {
            "task_id": task_id,
            "finished": result.finished,
            "output": result.output_text,
            "token_total_delta": result.token_total_delta,
        }
        
    except Exception as exc:
        logger.error(f"OpenManus task {task_id} failed: {exc}")
        from . import db
        db.update_task_fields(task_id, status="error", last_error=str(exc))
        db.add_event(task_id, "error", "task.failed", f"Execution error: {str(exc)}")
        raise

# ═══ Connector Tasks ═══
@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="manus_pro_server.tasks.connector_sync",
    max_retries=3,
)
def connector_sync(self, connector_id: str, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    مزامنة موصل
    
    Args:
        connector_id: معرف الموصل
        action: الإجراء (send, fetch, sync)
        payload: البيانات
    
    Returns:
        نتيجة المزامنة
    """
    try:
        from .connectors import get_connector
        
        logger.info(f"Connector sync: {connector_id} - {action}")
        
        connector = get_connector(connector_id)
        
        if action == "send":
            result = connector.send(payload)
        elif action == "fetch":
            result = connector.fetch(payload)
        elif action == "sync":
            result = connector.sync()
        else:
            raise ValueError(f"Unknown action: {action}")
        
        logger.info(f"Connector sync completed: {connector_id}")
        return result
        
    except Exception as exc:
        logger.error(f"Connector sync failed: {connector_id} - {exc}")
        raise

@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="manus_pro_server.tasks.refresh_connector_tokens",
)
def refresh_connector_tokens(self) -> Dict[str, Any]:
    """
    تحديث رموز OAuth للموصلات
    
    Returns:
        عدد الموصلات المحدثة
    """
    try:
        from .connectors import refresh_all_tokens
        
        logger.info("Refreshing connector OAuth tokens")
        
        refreshed_count = refresh_all_tokens()
        
        logger.info(f"Refreshed {refreshed_count} connector tokens")
        return {"refreshed": refreshed_count}
        
    except Exception as exc:
        logger.error(f"Token refresh failed: {exc}")
        raise

# ═══ Cleanup Tasks ═══
@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="manus_pro_server.tasks.cleanup_old_tasks",
)
def cleanup_old_tasks(self, days: int = 30) -> Dict[str, Any]:
    """
    تنظيف المهام القديمة
    
    Args:
        days: عدد الأيام (المهام الأقدم من هذا سيتم حذفها)
    
    Returns:
        عدد المهام المحذوفة
    """
    try:
        from . import db
        
        logger.info(f"Cleaning up tasks older than {days} days")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # حذف المهام المكتملة القديمة
        deleted_count = db.delete_old_tasks(cutoff_date)
        
        logger.info(f"Deleted {deleted_count} old tasks")
        return {"deleted": deleted_count}
        
    except Exception as exc:
        logger.error(f"Cleanup old tasks failed: {exc}")
        raise

@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="manus_pro_server.tasks.cleanup_expired_attachments",
)
def cleanup_expired_attachments(self) -> Dict[str, Any]:
    """
    تنظيف المرفقات المنتهية
    
    Returns:
        عدد المرفقات المحذوفة
    """
    try:
        from .s3_storage import cleanup_expired_attachments as cleanup_s3
        
        logger.info("Cleaning up expired attachments")
        
        deleted_count = cleanup_s3()
        
        logger.info(f"Deleted {deleted_count} expired attachments")
        return {"deleted": deleted_count}
        
    except Exception as exc:
        logger.error(f"Cleanup expired attachments failed: {exc}")
        raise

# ═══ System Health Check ═══
@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="manus_pro_server.tasks.system_health_check",
)
def system_health_check(self) -> Dict[str, Any]:
    """
    فحص صحة النظام
    
    Returns:
        تقرير الصحة
    """
    try:
        from . import db
        from .s3_storage import check_storage_health
        
        logger.info("Running system health check")
        
        # فحص قاعدة البيانات
        db_healthy = db.check_health()
        
        # فحص التخزين
        storage_healthy = check_storage_health()
        
        # فحص Redis
        redis_healthy = celery_app.backend.ping()
        
        health_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_healthy,
            "storage": storage_healthy,
            "redis": redis_healthy,
            "overall": db_healthy and storage_healthy and redis_healthy,
        }
        
        if not health_report["overall"]:
            logger.warning(f"System health check failed: {health_report}")
        else:
            logger.info("System health check passed")
        
        return health_report
        
    except Exception as exc:
        logger.error(f"System health check failed: {exc}")
        raise

# ═══ File Scanning ═══
@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="manus_pro_server.tasks.scan_file",
    max_retries=3,
)
def scan_file(self, object_key: str) -> Dict[str, Any]:
    """
    فحص ملف مرفوع ضد التهديدات (MVP)
    
    Args:
        object_key: مفتاح الملف في S3
    
    Returns:
        نتيجة الفحص
    """
    try:
        from .s3_storage import download_file_to_tmp
        import os
        import subprocess
        
        logger.info(f"Scanning file: {object_key}")
        
        # تحميل الملف إلى مجلد مؤقت
        tmp_path = download_file_to_tmp(object_key)
        
        try:
            # محاولة استخدام ClamAV إذا كان متاحاً
            result = subprocess.run(
                ["clamscan", "--no-summary", tmp_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                scan_result = {
                    "status": "clean",
                    "scanner": "clamav",
                    "object_key": object_key
                }
            else:
                # تم اكتشاف تهديد
                scan_result = {
                    "status": "threat_detected",
                    "scanner": "clamav",
                    "object_key": object_key,
                    "details": result.stdout
                }
                
                # نقل الملف إلى الحجر الصحي
                from .s3_storage import move_to_quarantine
                move_to_quarantine(object_key)
                
                logger.warning(f"Threat detected in file: {object_key}")
                
        except FileNotFoundError:
            # ClamAV غير متاح، وضع علامة كممسوح (mock)
            logger.warning("ClamAV not available, marking as scanned (mock)")
            scan_result = {
                "status": "scanned",
                "scanner": "mock",
                "object_key": object_key,
                "note": "ClamAV not available"
            }
        
        finally:
            # حذف الملف المؤقت
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
        logger.info(f"File scan completed: {object_key} - {scan_result['status']}")
        return scan_result
        
    except Exception as exc:
        logger.error(f"File scan failed: {object_key} - {exc}")
        raise

# ═══ Attachment Processing ═══
@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="manus_pro_server.tasks.process_attachment",
    max_retries=3,
)
def process_attachment(
    self,
    attachment_id: str,
    task_id: str,
    file_path: str,
    mime_type: str
) -> Dict[str, Any]:
    """
    معالجة مرفق (رفع إلى S3، استخراج metadata، إلخ)
    
    Args:
        attachment_id: معرف المرفق
        task_id: معرف المهمة
        file_path: مسار الملف المحلي
        mime_type: نوع MIME
    
    Returns:
        معلومات المرفق المعالج
    """
    try:
        from .s3_storage import upload_file
        from . import db
        
        logger.info(f"Processing attachment: {attachment_id}")
        
        # رفع الملف إلى S3
        storage_info = upload_file(file_path, attachment_id, mime_type)
        
        
        db.update_attachment(
            attachment_id,
            storage_key=storage_info["key"],
            storage_url=storage_info["url"],
        )
        
        logger.info(f"Attachment processed: {attachment_id}")
        return storage_info
        
    except Exception as exc:
        logger.error(f"Attachment processing failed: {attachment_id} - {exc}")
        raise
