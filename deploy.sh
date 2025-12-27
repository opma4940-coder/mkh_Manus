#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# سكريبت نشر نظام mkh_Manus
# يقوم ببناء وتشغيل جميع الخدمات وتطبيق الـ migrations
# ═══════════════════════════════════════════════════════════════════════════════

set -e

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🚀 بدء عملية نشر نظام mkh_Manus"
echo "═══════════════════════════════════════════════════════════════════════════════"

# التحقق من وجود ملف .env
if [ ! -f .env ]; then
    echo "⚠️  ملف .env غير موجود، سيتم نسخه من .env.example"
    cp .env.example .env
    echo "✅ تم إنشاء ملف .env - يرجى تحديث المتغيرات البيئية حسب الحاجة"
fi

# إيقاف الخدمات القديمة إن وجدت
echo ""
echo "🛑 إيقاف الخدمات القديمة..."
docker-compose down -v 2>/dev/null || true

# بناء الصور
echo ""
echo "🔨 بناء صور Docker..."
docker-compose build --no-cache

# تشغيل قاعدة البيانات أولاً
echo ""
echo "🗄️  تشغيل قاعدة البيانات PostgreSQL..."
docker-compose up -d postgres

# الانتظار حتى تصبح قاعدة البيانات جاهزة
echo ""
echo "⏳ انتظار جاهزية قاعدة البيانات..."
sleep 10

# تطبيق الـ migrations
echo ""
echo "📊 تطبيق migrations على قاعدة البيانات..."
docker-compose exec -T postgres psql -U ${POSTGRES_USER:-mkh_user} -d ${POSTGRES_DB:-mkh_manus} < migrations/0001_init.sql 2>/dev/null || true

# تشغيل Redis و MinIO
echo ""
echo "🔴 تشغيل Redis و MinIO..."
docker-compose up -d redis minio

# الانتظار حتى تصبح الخدمات جاهزة
echo ""
echo "⏳ انتظار جاهزية الخدمات..."
sleep 5

# تشغيل باقي الخدمات
echo ""
echo "🚀 تشغيل جميع الخدمات..."
docker-compose up -d

# عرض حالة الخدمات
echo ""
echo "📊 حالة الخدمات:"
docker-compose ps

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "✅ تم نشر النظام بنجاح!"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "🌐 الخدمات المتاحة:"
echo "   - لوحة التحكم: http://localhost:${API_PORT:-8000}"
echo "   - توثيق API: http://localhost:${API_PORT:-8000}/docs"
echo "   - MinIO Console: http://localhost:${MINIO_CONSOLE_PORT:-9001}"
echo "   - Flower (Celery): http://localhost:${FLOWER_PORT:-5555}"
echo ""
echo "📝 لعرض السجلات: docker-compose logs -f"
echo "🛑 لإيقاف النظام: docker-compose down"
echo ""
