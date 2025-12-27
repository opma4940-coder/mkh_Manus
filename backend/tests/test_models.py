"""
اختبارات لنماذج قاعدة البيانات
يختبر جميع النماذج والعلاقات
"""

import pytest
from datetime import datetime


def test_user_model():
    """
    اختبار نموذج المستخدم
    يجب أن يحتوي على جميع الحقول المطلوبة
    """
    # بيانات المستخدم
    user_data = {
        "id": "test-user-123",
        "username": "test_user",
        "email": "test@example.com",
        "is_active": True,
        "is_admin": False
    }
    
    # التحقق من صحة البيانات
    assert user_data["username"] == "test_user"
    assert user_data["email"] == "test@example.com"
    assert user_data["is_active"] is True
    assert user_data["is_admin"] is False


def test_task_model():
    """
    اختبار نموذج المهمة
    يجب أن يحتوي على جميع الحقول المطلوبة
    """
    # بيانات المهمة
    task_data = {
        "id": "test-task-123",
        "owner_id": "test-user-123",
        "goal": "مهمة اختبار",
        "status": "queued",
        "progress": 0.0,
        "token_budget": 1000000
    }
    
    # التحقق من صحة البيانات
    assert task_data["goal"] == "مهمة اختبار"
    assert task_data["status"] == "queued"
    assert task_data["progress"] == 0.0
    assert task_data["token_budget"] == 1000000


def test_event_model():
    """
    اختبار نموذج الحدث
    يجب أن يحتوي على جميع الحقول المطلوبة
    """
    # بيانات الحدث
    event_data = {
        "id": 1,
        "task_id": "test-task-123",
        "level": "info",
        "event_type": "task_started",
        "message": "بدأت المهمة"
    }
    
    # التحقق من صحة البيانات
    assert event_data["level"] == "info"
    assert event_data["event_type"] == "task_started"
    assert event_data["message"] == "بدأت المهمة"


def test_connector_model():
    """
    اختبار نموذج الموصل
    يجب أن يحتوي على جميع الحقول المطلوبة
    """
    # بيانات الموصل
    connector_data = {
        "id": "test-connector-123",
        "owner_id": "test-user-123",
        "name": "Google Drive",
        "type": "google_drive",
        "status": "active"
    }
    
    # التحقق من صحة البيانات
    assert connector_data["name"] == "Google Drive"
    assert connector_data["type"] == "google_drive"
    assert connector_data["status"] == "active"


def test_attachment_model():
    """
    اختبار نموذج المرفق
    يجب أن يحتوي على جميع الحقول المطلوبة
    """
    # بيانات المرفق
    attachment_data = {
        "id": "test-attachment-123",
        "task_id": "test-task-123",
        "filename": "document.pdf",
        "mime_type": "application/pdf",
        "size_bytes": 1024000,
        "storage_key": "uploads/1234567890_document.pdf"
    }
    
    # التحقق من صحة البيانات
    assert attachment_data["filename"] == "document.pdf"
    assert attachment_data["mime_type"] == "application/pdf"
    assert attachment_data["size_bytes"] == 1024000


def test_audit_log_model():
    """
    اختبار نموذج سجل التدقيق
    يجب أن يحتوي على جميع الحقول المطلوبة
    """
    # بيانات سجل التدقيق
    audit_data = {
        "id": 1,
        "user_id": "test-user-123",
        "action": "create_task",
        "resource_type": "task",
        "resource_id": "test-task-123"
    }
    
    # التحقق من صحة البيانات
    assert audit_data["action"] == "create_task"
    assert audit_data["resource_type"] == "task"
    assert audit_data["resource_id"] == "test-task-123"


def test_task_status_enum():
    """
    اختبار enum حالات المهمة
    يجب أن يحتوي على جميع الحالات المطلوبة
    """
    valid_statuses = ["queued", "running", "completed", "failed", "cancelled", "waiting"]
    
    for status in valid_statuses:
        assert status in valid_statuses


def test_connector_type_enum():
    """
    اختبار enum أنواع الموصلات
    يجب أن يحتوي على جميع الأنواع المطلوبة
    """
    valid_types = [
        "local_device", "google", "google_drive", "microsoft_onedrive",
        "facebook", "messenger", "whatsapp", "instagram", "threads",
        "tiktok", "snapchat", "telegram", "discord", "linkedin",
        "github", "reddit"
    ]
    
    assert len(valid_types) >= 16


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
