#!/bin/bash
# FILE: docker-entrypoint.sh
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                    نقطة الدخول المحسّنة لحاوية API                          ║
# ║                                                                              ║
# ║  الوصف:                                                                     ║
# ║  - تهيئة الأذونات والمجلدات                                                ║
# ║  - انتظار جاهزية قاعدة البيانات                                            ║
# ║  - تشغيل الخادم بشكل آمن                                                   ║
# ║                                                                              ║
# ║  التاريخ: ديسمبر 2025                                                       ║
# ║  الإصدار: 1.0                                                               ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

set -e

echo "═══════════════════════════════════════════════════════════"
echo "  Starting mkh_Manus API Server"
echo "═══════════════════════════════════════════════════════════"

# التأكد من وجود المجلدات المطلوبة
echo "→ Creating required directories..."
mkdir -p /app/data /app/workspace
chmod 755 /app/workspace
chmod 700 /app/data

# عرض معلومات البيئة
echo "→ Environment:"
echo "  PYTHONPATH: $PYTHONPATH"
echo "  Working Directory: $(pwd)"
echo "  Python Version: $(python3 --version)"

# التحقق من الملفات المطلوبة
echo "→ Checking required files..."
if [ ! -f "/app/run_server.py" ]; then
    echo "ERROR: /app/run_server.py not found!"
    exit 1
fi

if [ ! -d "/app/backend/src/manus_pro_server" ]; then
    echo "ERROR: /app/backend/src/manus_pro_server not found!"
    exit 1
fi

echo "  ✓ All required files present"

# انتظار جاهزية PostgreSQL (إذا كان مستخدماً)
if [ -n "$POSTGRES_HOST" ]; then
    echo "→ Waiting for PostgreSQL..."
    max_attempts=30
    attempt=0
    until pg_isready -h "$POSTGRES_HOST" -p "${POSTGRES_PORT:-5432}" -U "$POSTGRES_USER" || [ $attempt -eq $max_attempts ]; do
        attempt=$((attempt + 1))
        echo "  Attempt $attempt/$max_attempts..."
        sleep 2
    done
    
    if [ $attempt -eq $max_attempts ]; then
        echo "WARNING: PostgreSQL not ready after $max_attempts attempts, continuing anyway..."
    else
        echo "  ✓ PostgreSQL is ready"
    fi
fi

# انتظار جاهزية Redis
if [ -n "$REDIS_HOST" ]; then
    echo "→ Waiting for Redis..."
    max_attempts=15
    attempt=0
    until redis-cli -h "$REDIS_HOST" -p "${REDIS_PORT:-6379}" ping 2>/dev/null | grep -q PONG || [ $attempt -eq $max_attempts ]; do
        attempt=$((attempt + 1))
        echo "  Attempt $attempt/$max_attempts..."
        sleep 1
    done
    
    if [ $attempt -eq $max_attempts ]; then
        echo "WARNING: Redis not ready after $max_attempts attempts, continuing anyway..."
    else
        echo "  ✓ Redis is ready"
    fi
fi

echo "→ Starting Python server..."
echo "═══════════════════════════════════════════════════════════"

# تشغيل الخادم
exec python3 /app/run_server.py
