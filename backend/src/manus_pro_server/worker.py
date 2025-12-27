# محرك تنفيذ المهام في الخلفية لنظام mkh_Manus:
# - يقوم بمراقبة قاعدة البيانات لجلب المهام المجدولة (Queued).
# - يدير دورة حياة تنفيذ المهمة عبر التواصل مع OpenManus Bridge.
# - يدعم إلغاء المهام فوراً عند طلب المستخدم.
# - مصمم ليكون تنفيذياً بنسبة 100% وجاهزاً للإنتاج الفعلي في ديسمبر 2025.

from __future__ import annotations
import asyncio
import math
import time
import traceback
from typing import Any, Dict, Optional

from . import db
from .config import (
    CYCLE_STEPS_DEFAULT,
    RUNTIME_POLL_INTERVAL_SEC,
    TOKEN_SOFT_BUDGET_FRACTION,
    API_KEY_SLOTS,
)
from .openmanus_bridge import run_openmanus_cycle
from .logging_config import get_logger

logger = get_logger(__name__)

def _now_iso() -> str:
    """الحصول على الوقت الحالي بتنسيق ISO 8601."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

async def process_one_cycle(task: Dict[str, Any]) -> None:
    """معالجة دورة عمل واحدة لمهمة محددة."""
    task_id = task["id"]
    
    # 1. التحقق من طلب الإلغاء
    if int(task.get("cancel_requested") or 0) == 1:
        db.update_task_fields(task_id, status="cancelled", completed_at=_now_iso())
        db.add_event(task_id, "warning", "task.cancelled", "Task cancelled by user.")
        logger.info(f"Task {task_id} cancelled by user.")
        return

    # 2. تحميل مفاتيح API
    available_keys = {}
    for slot in API_KEY_SLOTS:
        val = db.get_setting(slot)
        if val: available_keys[slot] = val
    
    if not available_keys:
        db.update_task_fields(task_id, status="waiting", last_error="No API keys configured.")
        db.add_event(task_id, "error", "settings.missing_keys", "Please add API keys in settings.")
        logger.warning(f"Task {task_id} waiting for API keys.")
        return

    # 3. بدء أو استئناف المهمة
    if not task.get("started_at"):
        db.update_task_fields(task_id, status="running", started_at=_now_iso())
        db.add_event(task_id, "info", "task.started", "Task execution started.")
        logger.info(f"Task {task_id} started.")

    # 4. تنفيذ دورة العمل عبر الجسر
    state = task["state_json"]
    prior_messages = state.get("openmanus", {}).get("messages", [])
    
    t0 = time.time()
    try:
        res = await run_openmanus_cycle(
            task_id=task_id,
            available_api_keys=available_keys,
            goal=task["goal"],
            project_path=task["project_path"],
            cycle_steps=CYCLE_STEPS_DEFAULT,
            prior_messages=prior_messages
        )
    except Exception as e:
        logger.error(f"Cycle execution failed for task {task_id}: {str(e)}")
        db.update_task_fields(task_id, status="error", last_error=str(e))
        db.add_event(task_id, "error", "cycle.failed", f"Execution error: {str(e)}")
        return

    duration = time.time() - t0

    state.setdefault("checkpoints", [])
    state["openmanus"]["messages"] = res.messages
    state["checkpoints"].append({"ts": _now_iso(), "duration": duration, "finished": res.finished})
    
    token_total = int(task.get("token_total") or 0) + res.token_total_delta
    steps_done = int(task.get("steps_done") or 0) + CYCLE_STEPS_DEFAULT
    steps_estimate = int(task.get("steps_estimate") or 20)
    
    # تقدير ديناميكي للتقدم
    if steps_done >= steps_estimate: steps_estimate += 10
    progress = min(0.99, steps_done / steps_estimate)
    if res.finished: progress = 1.0

    db.set_task_state(task_id, state)
    db.update_task_fields(
        task_id,
        status="completed" if res.finished else "running",
        progress=progress,
        steps_done=steps_done,
        steps_estimate=steps_estimate,
        token_total=token_total,
        completed_at=_now_iso() if res.finished else None
    )

    db.add_event(
        task_id, 
        "info", 
        "cycle.completed", 
        f"Cycle finished in {duration:.2f}s", 
        data={"output": res.output_text[:1000] if res.output_text else ""}
    )
    logger.info(f"Task {task_id} cycle completed. Status: {'Finished' if res.finished else 'Running'}")

async def main() -> None:
    """نقطة الدخول الرئيسية للعامل."""
    db.init_db()
    logger.info("mkh_Manus Task Worker started and ready.")
    
    while True:
        try:
            task = db.fetch_next_runnable_task()
            if not task:
                await asyncio.sleep(RUNTIME_POLL_INTERVAL_SEC)
                continue
            
            await process_one_cycle(task)
            
        except Exception as e:
            logger.error(f"Worker critical error: {str(e)}")
            traceback.print_exc()
            await asyncio.sleep(5) # الانتظار عند حدوث خطأ حرج
            
        await asyncio.sleep(0.1) # راحة بسيطة بين المهام

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user.")
