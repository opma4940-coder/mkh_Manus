#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# اختبار البناء والتشغيل الشامل
# يختبر عملية البناء الكاملة باستخدام Docker Compose
# ═══════════════════════════════════════════════════════════════════════════════

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🔨 اختبار البناء والتشغيل الشامل"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

FAILED=0
TOTAL_TESTS=0

# دالة لتسجيل نتيجة الاختبار
log_test() {
    local test_name="$1"
    local result="$2"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ "$result" = "pass" ]; then
        echo "✅ [$TOTAL_TESTS] $test_name"
    else
        echo "❌ [$TOTAL_TESTS] $test_name"
        FAILED=$((FAILED + 1))
    fi
}

# ═══ المرحلة 1: التحقق من المتطلبات ═══
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 المرحلة 1: التحقق من المتطلبات الأساسية"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# اختبار 1: وجود Docker
if command -v docker &> /dev/null; then
    log_test "وجود Docker" "pass"
else
    log_test "وجود Docker" "fail"
fi

# اختبار 2: وجود Docker Compose
if command -v docker-compose &> /dev/null; then
    log_test "وجود Docker Compose" "pass"
else
    log_test "وجود Docker Compose" "fail"
fi

# اختبار 3: وجود ملف docker-compose.yml
if [ -f "docker-compose.yml" ]; then
    log_test "وجود ملف docker-compose.yml" "pass"
else
    log_test "وجود ملف docker-compose.yml" "fail"
fi

# اختبار 4: وجود Dockerfile
if [ -f "Dockerfile" ]; then
    log_test "وجود Dockerfile" "pass"
else
    log_test "وجود Dockerfile" "fail"
fi

# اختبار 5: وجود ملف .env
if [ -f ".env" ]; then
    log_test "وجود ملف .env" "pass"
else
    log_test "وجود ملف .env" "fail"
    echo "⚠️  تحذير: يجب إنشاء ملف .env من .env.example"
fi

# ═══ المرحلة 2: التحقق من صحة الملفات ═══
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📄 المرحلة 2: التحقق من صحة ملفات التكوين"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# اختبار 6: صحة docker-compose.yml
if docker-compose config > /dev/null 2>&1; then
    log_test "صحة ملف docker-compose.yml" "pass"
else
    log_test "صحة ملف docker-compose.yml" "fail"
fi

# اختبار 7: وجود جميع المجلدات المطلوبة
REQUIRED_DIRS=("backend" "frontend" "migrations" "scripts")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        log_test "وجود مجلد $dir" "pass"
    else
        log_test "وجود مجلد $dir" "fail"
    fi
done

# ═══ المرحلة 3: بناء الصور ═══
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏗️  المرحلة 3: بناء صور Docker"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# اختبار 11: بناء جميع الصور
if docker-compose build --no-cache > /tmp/build.log 2>&1; then
    log_test "بناء جميع صور Docker" "pass"
else
    log_test "بناء جميع صور Docker" "fail"
    echo "⚠️  راجع السجل: /tmp/build.log"
fi

# ═══ المرحلة 4: تشغيل الخدمات ═══
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 المرحلة 4: تشغيل جميع الخدمات"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# اختبار 12: تشغيل جميع الخدمات
if docker-compose up -d > /tmp/up.log 2>&1; then
    log_test "تشغيل جميع الخدمات" "pass"
else
    log_test "تشغيل جميع الخدمات" "fail"
    echo "⚠️  راجع السجل: /tmp/up.log"
fi

# الانتظار لبدء الخدمات
echo "⏳ انتظار بدء الخدمات (30 ثانية)..."
sleep 30

# ═══ المرحلة 5: التحقق من تشغيل الحاويات ═══
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐳 المرحلة 5: التحقق من تشغيل الحاويات"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# قائمة الخدمات المتوقعة
SERVICES=("postgres" "redis" "minio" "api" "worker" "flower")

for service in "${SERVICES[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        log_test "تشغيل حاوية $service" "pass"
    else
        log_test "تشغيل حاوية $service" "fail"
    fi
done

# ═══ المرحلة 6: التحقق من صحة الخدمات ═══
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 المرحلة 6: التحقق من صحة الخدمات"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# اختبار 18: PostgreSQL
if docker-compose exec -T postgres pg_isready > /dev/null 2>&1; then
    log_test "صحة خدمة PostgreSQL" "pass"
else
    log_test "صحة خدمة PostgreSQL" "fail"
fi

# اختبار 19: Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    log_test "صحة خدمة Redis" "pass"
else
    log_test "صحة خدمة Redis" "fail"
fi

# اختبار 20: MinIO
if curl -s http://localhost:9000/minio/health/live > /dev/null 2>&1; then
    log_test "صحة خدمة MinIO" "pass"
else
    log_test "صحة خدمة MinIO" "fail"
fi

# ═══ النتائج النهائية ═══
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
if [ $FAILED -eq 0 ]; then
    echo "✅ نجحت جميع الاختبارات! ($TOTAL_TESTS/$TOTAL_TESTS)"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    exit 0
else
    echo "❌ فشل $FAILED من $TOTAL_TESTS اختبار"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    exit 1
fi
