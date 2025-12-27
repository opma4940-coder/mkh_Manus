#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# سكريبت تشغيل جميع الاختبارات
# يشغل جميع اختبارات النظام بالترتيب ويجمع النتائج
# ═══════════════════════════════════════════════════════════════════════════════

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🧪 تشغيل جميع اختبارات نظام mkh_Manus"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📅 التاريخ: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📂 المسار: $PROJECT_ROOT"
echo ""

# متغيرات لتتبع النتائج
TOTAL_TEST_SUITES=0
PASSED_TEST_SUITES=0
FAILED_TEST_SUITES=0
RESULTS_FILE="$PROJECT_ROOT/tests/test_results_$(date +%Y%m%d_%H%M%S).txt"

# دالة لتشغيل مجموعة اختبارات
run_test_suite() {
    local test_name="$1"
    local test_script="$2"
    local test_type="${3:-bash}"
    
    TOTAL_TEST_SUITES=$((TOTAL_TEST_SUITES + 1))
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "▶️  تشغيل: $test_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    local start_time=$(date +%s)
    
    if [ "$test_type" = "bash" ]; then
        if bash "$test_script" 2>&1 | tee -a "$RESULTS_FILE"; then
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            echo ""
            echo "✅ نجح: $test_name (المدة: ${duration}s)"
            echo "✅ نجح: $test_name (المدة: ${duration}s)" >> "$RESULTS_FILE"
            PASSED_TEST_SUITES=$((PASSED_TEST_SUITES + 1))
            return 0
        else
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            echo ""
            echo "❌ فشل: $test_name (المدة: ${duration}s)"
            echo "❌ فشل: $test_name (المدة: ${duration}s)" >> "$RESULTS_FILE"
            FAILED_TEST_SUITES=$((FAILED_TEST_SUITES + 1))
            return 1
        fi
    elif [ "$test_type" = "node" ]; then
        if node "$test_script" 2>&1 | tee -a "$RESULTS_FILE"; then
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            echo ""
            echo "✅ نجح: $test_name (المدة: ${duration}s)"
            echo "✅ نجح: $test_name (المدة: ${duration}s)" >> "$RESULTS_FILE"
            PASSED_TEST_SUITES=$((PASSED_TEST_SUITES + 1))
            return 0
        else
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            echo ""
            echo "❌ فشل: $test_name (المدة: ${duration}s)"
            echo "❌ فشل: $test_name (المدة: ${duration}s)" >> "$RESULTS_FILE"
            FAILED_TEST_SUITES=$((FAILED_TEST_SUITES + 1))
            return 1
        fi
    fi
    
    echo ""
}

# بدء ملف النتائج
echo "═══════════════════════════════════════════════════════════════════════════════" > "$RESULTS_FILE"
echo "نتائج اختبارات نظام mkh_Manus" >> "$RESULTS_FILE"
echo "التاريخ: $(date '+%Y-%m-%d %H:%M:%S')" >> "$RESULTS_FILE"
echo "═══════════════════════════════════════════════════════════════════════════════" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

# ═══ المرحلة 1: اختبارات البناء والتشغيل ═══
echo "🏗️  المرحلة 1: اختبارات البناء والتشغيل"
echo ""
run_test_suite "اختبار البناء والتشغيل" "$SCRIPT_DIR/test_build_and_deployment.sh" "bash" || true

# ═══ المرحلة 2: اختبارات المنافذ والخدمات ═══
echo ""
echo "🔌 المرحلة 2: اختبارات المنافذ والخدمات"
echo ""
run_test_suite "اختبار المنافذ والخدمات" "$SCRIPT_DIR/test_ports_and_services.sh" "bash" || true

# ═══ المرحلة 3: اختبارات API ═══
echo ""
echo "🔗 المرحلة 3: اختبارات API"
echo ""
run_test_suite "اختبار جميع API Endpoints" "$SCRIPT_DIR/test_api_endpoints.sh" "bash" || true

# ═══ المرحلة 4: اختبارات الوظائف ═══
echo ""
echo "⚙️  المرحلة 4: اختبارات الوظائف"
echo ""
run_test_suite "اختبار جميع الوظائف" "$SCRIPT_DIR/test_all_functions.sh" "bash" || true

# ═══ المرحلة 5: اختبارات التكامل ═══
echo ""
echo "🔗 المرحلة 5: اختبارات التكامل"
echo ""
run_test_suite "اختبار التكامل الشامل" "$SCRIPT_DIR/test_integration.sh" "bash" || true

# ═══ المرحلة 6: اختبارات الواجهة (إذا كان Node.js متوفراً) ═══
if command -v node &> /dev/null; then
    echo ""
    echo "🌐 المرحلة 6: اختبارات الواجهة الأمامية"
    echo ""
    
    # التحقق من تثبيت puppeteer
    if [ -d "$PROJECT_ROOT/node_modules/puppeteer" ] || npm list -g puppeteer &> /dev/null; then
        run_test_suite "اختبار مكونات الواجهة" "$SCRIPT_DIR/test_frontend_components.js" "node" || true
        run_test_suite "اختبار جميع الأزرار والأيقونات" "$SCRIPT_DIR/test_all_buttons_and_icons.js" "node" || true
    else
        echo "⚠️  تحذير: puppeteer غير مثبت، تخطي اختبارات الواجهة"
        echo "   لتثبيته: npm install -g puppeteer"
    fi
else
    echo "⚠️  تحذير: Node.js غير متوفر، تخطي اختبارات الواجهة"
fi

# ═══ النتائج النهائية ═══
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "📊 ملخص النتائج النهائي"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "إجمالي مجموعات الاختبارات: $TOTAL_TEST_SUITES"
echo "نجح: $PASSED_TEST_SUITES"
echo "فشل: $FAILED_TEST_SUITES"
echo ""

if [ $FAILED_TEST_SUITES -eq 0 ]; then
    echo "✅ نجحت جميع الاختبارات! 🎉"
    echo ""
    echo "تم حفظ النتائج في: $RESULTS_FILE"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    exit 0
else
    PASS_RATE=$((PASSED_TEST_SUITES * 100 / TOTAL_TEST_SUITES))
    echo "⚠️  فشل $FAILED_TEST_SUITES من $TOTAL_TEST_SUITES مجموعة اختبارات"
    echo "نسبة النجاح: ${PASS_RATE}%"
    echo ""
    echo "تم حفظ النتائج في: $RESULTS_FILE"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    exit 1
fi
