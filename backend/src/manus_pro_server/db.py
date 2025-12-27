# طبقة إدارة قاعدة البيانات لنظام mkh_Manus:
# - يستخدم SQLite مع تفعيل وضع WAL (Write-Ahead Logging) للأداء العالي.
# - يدير جداول المهام (Tasks)، الأحداث (Events)، والإعدادات (Settings).
# - يتضمن آليات لمعالجة التزامن ومنع القفل (Locking).
# - يوفر وظائف آمنة لتخزين واسترجاع البيانات الحساسة المشفرة.
# - مصمم ليكون تنفيذياً بنسبة 100% وجاهزاً للإنتاج الفعلي في ديسمبر 2025.

from __future__ import annotations
import sqlite3
import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional
import orjson
from .config import DB_PATH
from . import crypto
from .logging_config import get_logger

logger = get_logger(__name__)

def _now_iso() -> str:
    """الحصول على الوقت الحالي بتنسيق ISO 8601."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def _get_db_connection() -> sqlite3.Connection:
    """إنشاء اتصال بقاعدة البيانات مهيأ للإنتاج والتزامن العالي."""
    # تفعيل وضع WAL وزيادة المهلة الزمنية لمنع القفل
    c = sqlite3.connect(str(DB_PATH), timeout=60, check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL;")
    c.execute("PRAGMA synchronous=NORMAL;")
    c.execute("PRAGMA foreign_keys=ON;")
    c.execute("PRAGMA busy_timeout = 5000;") # ✅ إضافة مهلة الانتظار المطلوبة
    return c

@contextmanager
def conn() -> sqlite3.Connection:
    """مدير سياق للاتصال بقاعدة البيانات مع commit/rollback الصحيح."""
    c = _get_db_connection()
    # تغيير isolation_level لتفعيل المعاملات اليدوية
    c.isolation_level = 'DEFERRED'
    try:
        yield c
        c.commit()  # حفظ التغييرات عند النجاح
    except Exception as e:
        try:
            c.rollback()  # التراجع عند الفشل
        except Exception:
            pass
        logger.error(f"Database transaction failed: {e}")
        raise
    finally:
        try:
            c.close()
        except Exception:
            pass

def init_db() -> None:
    """تهيئة جداول قاعدة البيانات مع الفهارس اللازمة للأداء."""
    crypto.get_key() # التأكد من وجود مفتاح التشفير
    with conn() as c:
        c.executescript(
            """
            -- جدول الإعدادات (مفاتيح API وغيرها)
            CREATE TABLE IF NOT EXISTS settings (
              key TEXT PRIMARY KEY,
              value BLOB NOT NULL,
              updated_at TEXT NOT NULL
            );

            -- جدول المهام الرئيسية
            CREATE TABLE IF NOT EXISTS tasks (
              id TEXT PRIMARY KEY,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              status TEXT NOT NULL,
              goal TEXT NOT NULL,
              project_path TEXT NOT NULL,
              started_at TEXT,
              completed_at TEXT,
              cancel_requested INTEGER NOT NULL DEFAULT 0,
              last_error TEXT,
              progress REAL NOT NULL DEFAULT 0.0,
              elapsed_seconds REAL NOT NULL DEFAULT 0.0,
              eta_seconds REAL NOT NULL DEFAULT 0.0,
              steps_done INTEGER NOT NULL DEFAULT 0,
              steps_estimate INTEGER NOT NULL DEFAULT 20,
              token_input INTEGER NOT NULL DEFAULT 0,
              token_output INTEGER NOT NULL DEFAULT 0,
              token_total INTEGER NOT NULL DEFAULT 0,
              token_budget INTEGER NOT NULL DEFAULT 1000000,
              state_json BLOB NOT NULL
            );

            -- جدول الأحداث لتتبع التقدم التفصيلي
            CREATE TABLE IF NOT EXISTS events (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              task_id TEXT NOT NULL,
              ts TEXT NOT NULL,
              level TEXT NOT NULL,
              event_type TEXT NOT NULL,
              message TEXT NOT NULL,
              data_json BLOB,
              FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
            );

            -- فهارس لتحسين سرعة الاستعلام
            CREATE INDEX IF NOT EXISTS idx_events_task_id_id ON events(task_id, id);
            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
            """
        )
    logger.info(f"Database initialized and optimized at {DB_PATH}")

# --- Settings Operations ---
def set_setting(key: str, value: str) -> None:
    """حفظ إعداد مع تشفير القيمة آلياً."""
    encrypted_value = crypto.encrypt_str(value)
    with conn() as c:
        c.execute(
            "INSERT INTO settings(key,value,updated_at) VALUES(?,?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
            (key, encrypted_value, _now_iso()),
        )

def get_setting(key: str) -> Optional[str]:
    """استرجاع إعداد مع فك التشفير آلياً."""
    with conn() as c:
        row = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        if row is None: return None
        return crypto.decrypt_str(row["value"])

# --- Event Operations ---
def add_event(task_id: str, level: str, event_type: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
    """إضافة حدث جديد مرتبط بمهمة."""
    with conn() as c:
        c.execute(
            "INSERT INTO events(task_id,ts,level,event_type,message,data_json) VALUES(?,?,?,?,?,?)",
            (task_id, _now_iso(), level, event_type, message, None if data is None else orjson.dumps(data)),
        )

def list_events(task_id: str, after_id: int = 0, limit: int = 500) -> List[Dict[str, Any]]:
    """سرد الأحداث لمهمة معينة."""
    with conn() as c:
        rows = c.execute(
            "SELECT id, ts, level, event_type, message, data_json FROM events "
            "WHERE task_id=? AND id>? ORDER BY id ASC LIMIT ?",
            (task_id, after_id, limit),
        ).fetchall()
    return [{"id": int(r["id"]), "ts": r["ts"], "level": r["level"], "event_type": r["event_type"], 
             "message": r["message"], "data": None if r["data_json"] is None else orjson.loads(r["data_json"])} for r in rows]

# --- Task Operations ---
def create_task(task_id: str, goal: str, project_path: str, token_budget: int) -> None:
    """إنشاء مهمة جديدة في النظام."""
    now = _now_iso()
    initial_state = {"task_id": task_id, "checkpoints": [], "openmanus": {"messages": []}, "notes": []}
    with conn() as c:
        c.execute(
            "INSERT INTO tasks(id,created_at,updated_at,status,goal,project_path,token_budget,state_json) "
            "VALUES(?,?,?,?,?,?,?,?)",
            (task_id, now, now, "queued", goal, project_path, int(token_budget), orjson.dumps(initial_state)),
        )

def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    """الحصول على تفاصيل مهمة محددة."""
    with conn() as c:
        row = c.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if row is None: return None
    d = dict(row)
    d["state_json"] = orjson.loads(d["state_json"])
    return d

def list_tasks(limit: int = 200) -> List[Dict[str, Any]]:
    """سرد جميع المهام في النظام."""
    with conn() as c:
        rows = c.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    return [{**dict(r), "state_json": orjson.loads(r["state_json"])} for r in rows]

def update_task_fields(task_id: str, **fields: Any) -> None:
    if not fields: return
    fields["updated_at"] = _now_iso()
    cols = ", ".join([f'{k}=?' for k in fields.keys()])
    vals = list(fields.values()) + [task_id]
    with conn() as c:
        c.execute(f"UPDATE tasks SET {cols} WHERE id=?", vals)

def set_task_state(task_id: str, state_obj: Dict[str, Any]) -> None:
    update_task_fields(task_id, state_json=orjson.dumps(state_obj))

def request_cancel(task_id: str) -> None:
    """طلب إلغاء المهمة."""
    update_task_fields(task_id, cancel_requested=1)

def fetch_next_runnable_task() -> Optional[Dict[str, Any]]:
    """جلب المهمة التالية الجاهزة للتنفيذ من قبل العامل."""
    with conn() as c:
        row = c.execute(
            "SELECT * FROM tasks "
            "WHERE cancel_requested=0 AND status IN ('queued','running') "
            "ORDER BY CASE status WHEN 'queued' THEN 0 ELSE 1 END, updated_at ASC "
            "LIMIT 1"
        ).fetchone()
    if row is None: return None
    d = dict(row)
    d["state_json"] = orjson.loads(d["state_json"])
    return d
