# اختبارات Backend أساسية:
# - التأكد من أن API يعمل
# - إنشاء مهمة والتحقق من ظهورها
# - إضافة اختبارات لـ db.py و crypto.py (توصية التقرير)

import os
import tempfile
import time
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from manus_pro_server import db
from manus_pro_server import crypto
from manus_pro_server.api import app
from manus_pro_server.config import WORKSPACE_ROOT, FERNET_KEY_PATH

@pytest.fixture(autouse=True)
def _isolate_db(monkeypatch):
    """
    تهيئة قاعدة بيانات مؤقتة لكل اختبار
    """
    with tempfile.TemporaryDirectory() as td:
        # 1. DB Path
        db_path = Path(td) / "test.sqlite3"
        monkeypatch.setenv("MANUS_PRO_DB_PATH", str(db_path))
        
        # 2. Fernet Key Path
        fernet_key_path = Path(td) / "test.fernet.key"
        monkeypatch.setattr(crypto, "FERNET_KEY_PATH", fernet_key_path)
        
        # 3. إعادة تهيئة DB (التي ستولد مفتاح Fernet)
        db.init_db()
        yield

def test_settings_endpoint():
    c = TestClient(app)
    r = c.get("/api/settings")
    assert r.status_code == 200
    data = r.json()
    assert "models" in data
    assert "quotas" in data

def test_create_task():
    # ضمان وجود workspace root
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)

    c = TestClient(app)
    payload = {"goal": "اختبار مهمة", "project_path": ".", "token_budget": 100000}
    r = c.post("/api/tasks", json=payload)
    assert r.status_code == 200, r.text
    task = r.json()["task"]
    assert task["status"] == "queued"
    
    # التحقق من وجود المهمة في DB
    t = db.get_task(task["id"])
    assert t is not None
    assert t["goal"] == "اختبار مهمة"
    
    # التحقق من حدث الإنشاء
    events = db.list_events(task["id"])
    assert len(events) == 1
    assert events[0]["event_type"] == "task.queued"

def test_crypto_encryption_decryption():
    """
    اختبار تشفير وفك تشفير الأسرار
    """
    secret = "my_secret_api_key_12345"
    
    # تشفير
    encrypted = crypto.encrypt_str(secret)
    assert encrypted != secret
    assert encrypted.startswith("gAAAAA") # Fernet prefix (Base64 string)
    
    # فك تشفير
    decrypted = crypto.decrypt_str(encrypted)
    assert decrypted == secret

def test_db_settings_storage():
    """
    اختبار تخزين واسترجاع الإعدادات المشفرة
    """
    key = "test_setting_key"
    value = "test_setting_value"
    
    # تخزين
    db.set_setting(key, value)
    
    # استرجاع
    retrieved = db.get_setting(key)
    assert retrieved == value
    
    # التحقق من أن القيمة مخزنة مشفرة في DB
    conn = db._get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    db_value = cursor.fetchone()[0]
    conn.close()
    
    # يجب أن تكون القيمة في DB مشفرة
    assert db_value != value
    assert db_value.startswith("gAAAAA") # Fernet prefix (string)
    
    # التحقق من أن db.get_setting يفك التشفير تلقائياً
    assert crypto.decrypt_str(db_value) == value

def test_db_task_lifecycle():
    """
    اختبار دورة حياة المهمة في قاعدة البيانات
    """
    task_id = f"test_task_lifecycle_{uuid.uuid4().hex[:8]}"
    goal = "اختبار دورة حياة"
    
    # 1. إنشاء
    db.create_task(task_id, goal, ".", token_budget=50000)
    t = db.get_task(task_id)
    assert t["status"] == "queued"
    assert t["token_budget"] == 50000
    
    db.update_task_fields(task_id, status="running", steps_done=5, progress=0.25)
    t = db.get_task(task_id)
    assert t["status"] == "running"
    assert t["steps_done"] == 5
    assert t["progress"] == 0.25
    
    # 3. طلب إلغاء
    db.request_cancel(task_id)
    t = db.get_task(task_id)
    assert t["cancel_requested"] == 1
    
    state = {"openmanus": {"messages": [{"role": "user", "content": "hello"}]}}
    db.set_task_state(task_id, state)
    t = db.get_task(task_id)
    assert t["state_json"] == state
    
    # 5. جلب المهمة القابلة للتشغيل
    temp_task_id = f"temp_task_{uuid.uuid4().hex[:8]}"
    db.create_task(temp_task_id, "temp", ".", token_budget=1000)
    db.update_task_fields(temp_task_id, status="completed")   
    runnable = db.fetch_next_runnable_task()
    assert runnable is not None
    assert runnable["id"] == task_id
    
    # 6. جلب المهام
    tasks = db.list_tasks()
    assert len(tasks) == 1
    assert tasks[0]["id"] == task_id
    
    # 7. الأحداث
    db.add_event(task_id, "info", "test.event", "حدث اختبار")
    events = db.list_events(task_id)
    assert len(events) == 1
    assert events[0]["event_type"] == "test.event"
    
    # 8. جلب الأحداث بعد ID معين
    db.add_event(task_id, "info", "test.event2", "حدث اختبار 2")
    events_after = db.list_events(task_id, after_id=events[0]["id"])
    assert len(events_after) == 1
    assert events_after[0]["event_type"] == "test.event2"
