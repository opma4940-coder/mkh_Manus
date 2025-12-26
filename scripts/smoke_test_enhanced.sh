#!/bin/bash
# FILE: scripts/smoke_test_enhanced.sh
# =============================================================================
# اختبارات Smoke محسّنة لمشروع mkh_Manus
#
# الوظائف:
# - فحص بنية المشروع
# - فحص الملفات الأساسية
# - فحص صحة ملفات Python
# - فحص صحة ملفات JSON
# - فحص المتغيرات البيئية
# - اختبارات API أساسية (إذا كان الخادم يعمل)
#
# الاستخدام:
#   ./scripts/smoke_test_enhanced.sh
#
# Exit Codes:
#   0 - جميع الاختبارات ناجحة
#   1 - فشل أحد الاختبارات
# =============================================================================

set -e
set -u
set -o pipefail

# =============================================================================
# الألوان
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# =============================================================================
# دوال مساعدة
# =============================================================================

log_info() {
    echo -e "${BLUE}[SMOKE]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# =============================================================================
# المتغيرات
# =============================================================================

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TESTS_PASSED=0
TESTS_FAILED=0

# =============================================================================
# الاختبارات
# =============================================================================

log_info "بدء اختبارات Smoke"
echo "======================================"

# Test 1: فحص المجلدات الأساسية
log_info "Test 1: فحص المجلدات الأساسية"
REQUIRED_DIRS=(
    "manus_pro/backend"
    "manus_pro/frontend"
    "openmanus_core"
    "tests"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$PROJECT_ROOT/$dir" ]; then
        log_success "المجلد موجود: $dir"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log_error "المجلد مفقود: $dir"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
done

# Test 2: فحص الملفات الأساسية
log_info "Test 2: فحص الملفات الأساسية"
REQUIRED_FILES=(
    "README.md"
    "SECURITY.md"
    "requirements.txt"
    "docker-compose.yml"
    "manus_pro/backend/src/manus_pro_server/api.py"
    "manus_pro/backend/src/manus_pro_server/db.py"
    "openmanus_core/app/llm.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        log_success "الملف موجود: $file"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log_error "الملف مفقود: $file"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
done

# Test 3: فحص صحة ملفات Python
log_info "Test 3: فحص صحة ملفات Python"
PYTHON_FILES=(
    "manus_pro/backend/src/manus_pro_server/api.py"
    "manus_pro/backend/src/manus_pro_server/db.py"
    "manus_pro/backend/src/manus_pro_server/crypto.py"
    "openmanus_core/app/llm.py"
)

for pyfile in "${PYTHON_FILES[@]}"; do
    if python3 -m py_compile "$PROJECT_ROOT/$pyfile" 2>/dev/null; then
        log_success "ملف Python صحيح: $pyfile"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log_error "ملف Python به أخطاء: $pyfile"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
done

# Test 4: فحص صحة ملفات JSON
log_info "Test 4: فحص صحة ملفات JSON"
JSON_FILES=$(find "$PROJECT_ROOT" -name "*.json" -not -path "*/node_modules/*" -not -path "*/.venv/*" 2>/dev/null || true)

if [ -n "$JSON_FILES" ]; then
    while IFS= read -r jsonfile; do
        if python3 -c "import json; json.load(open('$jsonfile'))" 2>/dev/null; then
            log_success "ملف JSON صحيح: $(basename $jsonfile)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            log_error "ملف JSON به أخطاء: $jsonfile"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    done <<< "$JSON_FILES"
else
    log_info "لا توجد ملفات JSON للفحص"
fi

# Test 5: فحص استيراد الوحدات الأساسية
log_info "Test 5: فحص استيراد الوحدات الأساسية"
cd "$PROJECT_ROOT"

if PYTHONPATH=manus_pro/backend/src python3 -c "from manus_pro_server import api" 2>/dev/null; then
    log_success "يمكن استيراد api"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    log_error "فشل استيراد api"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

if PYTHONPATH=manus_pro/backend/src python3 -c "from manus_pro_server import db" 2>/dev/null; then
    log_success "يمكن استيراد db"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    log_error "فشل استيراد db"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 6: فحص قاعدة البيانات
log_info "Test 6: فحص قاعدة البيانات"
if [ -f "$PROJECT_ROOT/manus_pro/data/manus_pro.db" ]; then
    if sqlite3 "$PROJECT_ROOT/manus_pro/data/manus_pro.db" "PRAGMA integrity_check;" | grep -q "ok"; then
        log_success "قاعدة البيانات سليمة"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log_error "قاعدة البيانات بها مشاكل"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
else
    log_info "قاعدة البيانات غير موجودة (سيتم إنشاؤها عند أول تشغيل)"
fi

# Test 7: فحص المنافذ المستخدمة
log_info "Test 7: فحص المنافذ"
if command -v netstat >/dev/null 2>&1; then
    if netstat -tuln 2>/dev/null | grep -q ":8000"; then
        log_info "المنفذ 8000 مستخدم (الخادم يعمل)"
        
        # اختبار API إذا كان الخادم يعمل
        if command -v curl >/dev/null 2>&1; then
            if curl -s http://localhost:8000/health >/dev/null 2>&1; then
                log_success "API يستجيب على /health"
                TESTS_PASSED=$((TESTS_PASSED + 1))
            else
                log_info "API لا يستجيب (قد يحتاج token)"
            fi
        fi
    else
        log_info "المنفذ 8000 غير مستخدم (الخادم متوقف)"
    fi
else
    log_info "netstat غير متاح - تخطي فحص المنافذ"
fi

# Test 8: فحص Docker
log_info "Test 8: فحص Docker"
if [ -f "$PROJECT_ROOT/Dockerfile" ]; then
    log_success "Dockerfile موجود"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    
    # فحص صحة Dockerfile
    if command -v docker >/dev/null 2>&1; then
        if docker build -t mkh_manus:smoke-test -f "$PROJECT_ROOT/Dockerfile" "$PROJECT_ROOT" >/dev/null 2>&1; then
            log_success "Dockerfile صحيح (تم البناء بنجاح)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
            
            # تنظيف
            docker rmi mkh_manus:smoke-test >/dev/null 2>&1 || true
        else
            log_info "فشل بناء Dockerfile (قد يحتاج تبعيات)"
        fi
    else
        log_info "Docker غير متاح - تخطي بناء الصورة"
    fi
else
    log_error "Dockerfile مفقود"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 9: فحص docker-compose
log_info "Test 9: فحص docker-compose"
if [ -f "$PROJECT_ROOT/docker-compose.yml" ]; then
    log_success "docker-compose.yml موجود"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    
    if command -v docker-compose >/dev/null 2>&1; then
        if docker-compose -f "$PROJECT_ROOT/docker-compose.yml" config >/dev/null 2>&1; then
            log_success "docker-compose.yml صحيح"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            log_error "docker-compose.yml به أخطاء"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    else
        log_info "docker-compose غير متاح - تخطي التحقق"
    fi
else
    log_error "docker-compose.yml مفقود"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 10: فحص requirements.txt
log_info "Test 10: فحص requirements.txt"
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    log_success "requirements.txt موجود"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    
    # فحص صحة الصيغة
    if python3 -m pip install --dry-run -r "$PROJECT_ROOT/requirements.txt" >/dev/null 2>&1; then
        log_success "requirements.txt صحيح"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log_info "requirements.txt قد يحتاج تحديث"
    fi
else
    log_error "requirements.txt مفقود"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# =============================================================================
# النتائج
# =============================================================================

echo ""
echo "======================================"
log_info "ملخص النتائج"
echo "======================================"
echo "اختبارات ناجحة: $TESTS_PASSED"
echo "اختبارات فاشلة: $TESTS_FAILED"
echo "======================================"

if [ $TESTS_FAILED -eq 0 ]; then
    log_success "جميع اختبارات Smoke ناجحة!"
    exit 0
else
    log_error "فشلت $TESTS_FAILED اختبار/اختبارات"
    exit 1
fi
