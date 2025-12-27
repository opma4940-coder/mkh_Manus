# ═══════════════════════════════════════════════════════════════════════════════
# نماذج قاعدة البيانات PostgreSQL لنظام mkh_Manus
# يستخدم SQLAlchemy ORM مع دعم async
# التاريخ: ديسمبر 2025
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, 
    ForeignKey, Index, Enum as SQLEnum, JSON, LargeBinary
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

# ═══ Enums ═══
class TaskStatus(str, enum.Enum):
    """حالات المهمة"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING = "waiting"

class EventLevel(str, enum.Enum):
    """مستويات الأحداث"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ConnectorType(str, enum.Enum):
    """أنواع الموصلات"""
    LOCAL_DEVICE = "local_device"
    GOOGLE = "google"
    GOOGLE_DRIVE = "google_drive"
    MICROSOFT_ONEDRIVE = "microsoft_onedrive"
    FACEBOOK = "facebook"
    MESSENGER = "messenger"
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    THREADS = "threads"
    TIKTOK = "tiktok"
    SNAPCHAT = "snapchat"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    LINKEDIN = "linkedin"
    GITHUB = "github"
    REDDIT = "reddit"

class ConnectorStatus(str, enum.Enum):
    """حالات الموصل"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING_AUTH = "pending_auth"

# ═══ Models ═══

class User(Base):
    """نموذج المستخدم"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)
    
    # العلاقات
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")
    connectors = relationship("Connector", back_populates="owner", cascade="all, delete-orphan")
    settings = relationship("Setting", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

class Task(Base):
    """نموذج المهمة"""
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # معلومات أساسية
    goal = Column(Text, nullable=False)
    project_path = Column(String(500), nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.QUEUED, nullable=False, index=True)
    
    # التوقيتات
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # التحكم
    cancel_requested = Column(Boolean, default=False, nullable=False)
    last_error = Column(Text)
    
    # التقدم
    progress = Column(Float, default=0.0, nullable=False)
    elapsed_seconds = Column(Float, default=0.0, nullable=False)
    eta_seconds = Column(Float, default=0.0, nullable=False)
    steps_done = Column(Integer, default=0, nullable=False)
    steps_estimate = Column(Integer, default=20, nullable=False)
    
    # الرموز (Tokens)
    token_input = Column(Integer, default=0, nullable=False)
    token_output = Column(Integer, default=0, nullable=False)
    token_total = Column(Integer, default=0, nullable=False)
    token_budget = Column(Integer, default=1000000, nullable=False)
    
    # الحالة (JSON)
    state_json = Column(JSON, nullable=False)
    
    # العلاقات
    owner = relationship("User", back_populates="tasks")
    events = relationship("Event", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="task", cascade="all, delete-orphan")
    
    # الفهارس
    __table_args__ = (
        Index("idx_tasks_owner_status", "owner_id", "status"),
        Index("idx_tasks_status_updated", "status", "updated_at"),
    )

class Event(Base):
    """نموذج الحدث"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    
    ts = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    level = Column(SQLEnum(EventLevel), default=EventLevel.INFO, nullable=False)
    event_type = Column(String(100), nullable=False, index=True)
    message = Column(Text, nullable=False)
    data_json = Column(JSON)
    
    # العلاقات
    task = relationship("Task", back_populates="events")
    
    # الفهارس
    __table_args__ = (
        Index("idx_events_task_id_ts", "task_id", "ts"),
    )

class Setting(Base):
    """نموذج الإعدادات"""
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(255), nullable=False, index=True)
    value = Column(Text, nullable=False)  # مشفر
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # العلاقات
    user = relationship("User", back_populates="settings")
    
    # الفهارس
    __table_args__ = (
        Index("idx_settings_user_key", "user_id", "key", unique=True),
    )

class Connector(Base):
    """نموذج الموصل"""
    __tablename__ = "connectors"
    
    id = Column(String(36), primary_key=True)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    type = Column(SQLEnum(ConnectorType), nullable=False, index=True)
    status = Column(SQLEnum(ConnectorStatus), default=ConnectorStatus.PENDING_AUTH, nullable=False)
    
    # التكوين (مشفر)
    config_json = Column(JSON, nullable=False)
    
    # التوقيتات
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime)
    
    # العلاقات
    owner = relationship("User", back_populates="connectors")
    tokens = relationship("OAuthToken", back_populates="connector", cascade="all, delete-orphan")
    
    # الفهارس
    __table_args__ = (
        Index("idx_connectors_owner_type", "owner_id", "type"),
    )

class OAuthToken(Base):
    """نموذج رموز OAuth المشفرة"""
    __tablename__ = "oauth_tokens"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    connector_id = Column(String(36), ForeignKey("connectors.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # الرموز مشفرة باستخدام Fernet
    access_token_encrypted = Column(LargeBinary, nullable=False)
    refresh_token_encrypted = Column(LargeBinary, nullable=True)
    
    expires_at = Column(DateTime, nullable=True)
    scopes = Column(Text, nullable=True)
    
    # التوقيتات
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # العلاقات
    connector = relationship("Connector", back_populates="tokens")

class Attachment(Base):
    """نموذج المرفق"""
    __tablename__ = "attachments"
    
    id = Column(String(36), primary_key=True)
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # معلومات الملف
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    mime_type = Column(String(255), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    
    # التخزين (S3/MinIO)
    storage_key = Column(String(500), nullable=False, unique=True)
    storage_bucket = Column(String(255), nullable=False)
    storage_url = Column(Text)  # Signed URL (مؤقت)
    
    # التوقيتات
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime)  # للـ signed URLs
    
    # العلاقات
    task = relationship("Task", back_populates="attachments")

class AuditLog(Base):
    """نموذج سجل التدقيق"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    
    # معلومات الحدث
    action = Column(String(100), nullable=False, index=True)  # create_task, update_setting, delete_connector
    resource_type = Column(String(100), nullable=False)  # task, setting, connector
    resource_id = Column(String(36))
    
    # التفاصيل
    details_json = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # التوقيت
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # العلاقات
    user = relationship("User", back_populates="audit_logs")
    
    # الفهارس
    __table_args__ = (
        Index("idx_audit_logs_user_timestamp", "user_id", "timestamp"),
        Index("idx_audit_logs_action_timestamp", "action", "timestamp"),
    )
