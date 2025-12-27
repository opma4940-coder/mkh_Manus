-- ═══════════════════════════════════════════════════════════════════════════════
-- ملف الـ Migration الأولي لقاعدة بيانات mkh_Manus
-- يقوم بإنشاء جميع الجداول الأساسية للنظام
-- التاريخ: ديسمبر 2025
-- ═══════════════════════════════════════════════════════════════════════════════

-- جدول المستخدمين (Users)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL UNIQUE,
    email TEXT,
    password_hash TEXT,
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- جدول المهام (Tasks)
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    payload JSONB,
    status TEXT DEFAULT 'queued',
    priority INTEGER DEFAULT 0,
    idempotency_key TEXT UNIQUE,
    parent_task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ
);

-- فهرس لتسريع البحث عن المهام حسب المستخدم والحالة
CREATE INDEX IF NOT EXISTS idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);

-- جدول سجلات المهام (Task Logs)
CREATE TABLE IF NOT EXISTS task_logs (
    id SERIAL PRIMARY KEY,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    meta JSONB,
    timestamp TIMESTAMPTZ DEFAULT now(),
    actor TEXT,
    side_effects JSONB,
    output JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- فهرس لتسريع البحث في السجلات
CREATE INDEX IF NOT EXISTS idx_task_logs_task_id ON task_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_task_logs_timestamp ON task_logs(timestamp DESC);

-- جدول مفاتيح API (API Keys)
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    key_encrypted TEXT NOT NULL,
    key_masked TEXT NOT NULL,
    service TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    last_used_at TIMESTAMPTZ
);

-- فهرس لتسريع البحث عن المفاتيح
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);

-- جدول الملفات (Files)
CREATE TABLE IF NOT EXISTS files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    object_key TEXT NOT NULL UNIQUE,
    filename TEXT NOT NULL,
    size BIGINT NOT NULL,
    content_type TEXT NOT NULL,
    scanned BOOLEAN DEFAULT false,
    scan_result JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- فهرس لتسريع البحث عن الملفات
CREATE INDEX IF NOT EXISTS idx_files_user_id ON files(user_id);
CREATE INDEX IF NOT EXISTS idx_files_task_id ON files(task_id);
CREATE INDEX IF NOT EXISTS idx_files_created_at ON files(created_at DESC);

-- جدول الوكلاء (Agents)
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,
    status TEXT DEFAULT 'idle',
    capabilities JSONB,
    config JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- جدول تعيينات الوكلاء (Agent Assignments)
CREATE TABLE IF NOT EXISTS agent_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'assigned',
    assigned_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ
);

-- فهرس لتسريع البحث عن التعيينات
CREATE INDEX IF NOT EXISTS idx_agent_assignments_agent_id ON agent_assignments(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_assignments_task_id ON agent_assignments(task_id);

-- جدول الموصلات (Connectors)
CREATE TABLE IF NOT EXISTS connectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    credentials JSONB,
    config JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- فهرس لتسريع البحث عن الموصلات
CREATE INDEX IF NOT EXISTS idx_connectors_user_id ON connectors(user_id);

-- جدول الأحداث (Events)
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    event_data JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- فهرس لتسريع البحث عن الأحداث
CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_task_id ON events(task_id);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at DESC);

-- إنشاء مستخدم افتراضي (Admin)
INSERT INTO users (id, username, email, is_admin, password_hash)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'admin',
    'admin@mkh-manus.local',
    true,
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aeWZL8yQn8Pu'
)
ON CONFLICT (username) DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════════
-- انتهى ملف Migration
-- ═══════════════════════════════════════════════════════════════════════════════
