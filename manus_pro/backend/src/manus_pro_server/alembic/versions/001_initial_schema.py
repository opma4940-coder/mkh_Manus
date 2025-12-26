# ═══════════════════════════════════════════════════════════════════════════════
# الهجرة الأولى: إنشاء جداول قاعدة البيانات
# التاريخ: ديسمبر 2025
# ═══════════════════════════════════════════════════════════════════════════════

"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-12-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    """إنشاء الجداول"""
    
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('username', sa.String(255), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('is_admin', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime()),
    )
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_email', 'users', ['email'])
    
    # Tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('owner_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('goal', sa.Text(), nullable=False),
        sa.Column('project_path', sa.String(500), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('cancel_requested', sa.Boolean(), default=False, nullable=False),
        sa.Column('last_error', sa.Text()),
        sa.Column('progress', sa.Float(), default=0.0, nullable=False),
        sa.Column('elapsed_seconds', sa.Float(), default=0.0, nullable=False),
        sa.Column('eta_seconds', sa.Float(), default=0.0, nullable=False),
        sa.Column('steps_done', sa.Integer(), default=0, nullable=False),
        sa.Column('steps_estimate', sa.Integer(), default=20, nullable=False),
        sa.Column('token_input', sa.Integer(), default=0, nullable=False),
        sa.Column('token_output', sa.Integer(), default=0, nullable=False),
        sa.Column('token_total', sa.Integer(), default=0, nullable=False),
        sa.Column('token_budget', sa.Integer(), default=1000000, nullable=False),
        sa.Column('state_json', postgresql.JSON(), nullable=False),
    )
    op.create_index('idx_tasks_owner_id', 'tasks', ['owner_id'])
    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_created_at', 'tasks', ['created_at'])
    op.create_index('idx_tasks_owner_status', 'tasks', ['owner_id', 'status'])
    op.create_index('idx_tasks_status_updated', 'tasks', ['status', 'updated_at'])
    
    # Events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('task_id', sa.String(36), sa.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ts', sa.DateTime(), nullable=False),
        sa.Column('level', sa.String(20), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('data_json', postgresql.JSON()),
    )
    op.create_index('idx_events_task_id', 'events', ['task_id'])
    op.create_index('idx_events_ts', 'events', ['ts'])
    op.create_index('idx_events_task_id_ts', 'events', ['task_id', 'ts'])
    
    # Settings table
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('key', sa.String(255), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_settings_user_id', 'settings', ['user_id'])
    op.create_index('idx_settings_key', 'settings', ['key'])
    op.create_index('idx_settings_user_key', 'settings', ['user_id', 'key'], unique=True)
    
    # Connectors table
    op.create_table(
        'connectors',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('owner_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('config_json', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_used_at', sa.DateTime()),
    )
    op.create_index('idx_connectors_owner_id', 'connectors', ['owner_id'])
    op.create_index('idx_connectors_type', 'connectors', ['type'])
    op.create_index('idx_connectors_owner_type', 'connectors', ['owner_id', 'type'])
    
    # Attachments table
    op.create_table(
        'attachments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('task_id', sa.String(36), sa.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('filename', sa.String(500), nullable=False),
        sa.Column('original_filename', sa.String(500), nullable=False),
        sa.Column('mime_type', sa.String(255), nullable=False),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('storage_key', sa.String(500), nullable=False, unique=True),
        sa.Column('storage_bucket', sa.String(255), nullable=False),
        sa.Column('storage_url', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime()),
    )
    op.create_index('idx_attachments_task_id', 'attachments', ['task_id'])
    
    # Audit logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', sa.String(36)),
        sa.Column('details_json', postgresql.JSON()),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.Text()),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('idx_audit_logs_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('idx_audit_logs_user_timestamp', 'audit_logs', ['user_id', 'timestamp'])
    op.create_index('idx_audit_logs_action_timestamp', 'audit_logs', ['action', 'timestamp'])

def downgrade() -> None:
    """حذف الجداول"""
    op.drop_table('audit_logs')
    op.drop_table('attachments')
    op.drop_table('connectors')
    op.drop_table('settings')
    op.drop_table('events')
    op.drop_table('tasks')
    op.drop_table('users')
