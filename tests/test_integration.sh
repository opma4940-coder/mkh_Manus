#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# اختبار التكامل الشامل
# يختبر التكامل بين جميع مكونات النظام
# ═══════════════════════════════════════════════════════════════════════════════

set -e

API_BASE="http://localhost:8000"

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🔗 اختبار التكامل الشامل"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

FAILED=0
TOTAL_TESTS=0

log_test() {
    local test_name="$1"
    local result="$2"
    local details="${3:-}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ "$result" = "pass" ]; then
        echo "✅ [$TOTAL_TESTS] $test_name $details"
    else
        echo "❌ [$TOTAL_TESTS] $test_name $details"
        FAILED=$((FAILED + 1))
    fi
}

# ═══ سيناريو 1: رحلة المستخدم الكاملة ═══
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "👤 سيناريو 1: رحلة المستخدم الكاملة"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. تسجيل مستخدم جديد
TIMESTAMP=$(date +%s)
TEST_USER="testuser_$TIMESTAMP"
TEST_EMAIL="test_$TIMESTAMP@example.com"
TEST_PASSWORD="Test123!@#"

register_response=$(curl -s -X POST "$API_BASE/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$TEST_USER\",\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}" \
    -w "\n%{http_code}")
register_code=$(echo "$register_response" | tail -1)
if [ "$register_code" = "200" ] || [ "$register_code" = "201" ]; then
    log_test "1. تسجيل مستخدم جديد" "pass" "- المستخدم: $TEST_USER"
else
    log_test "1. تسجيل مستخدم جديد" "fail" "- كود: $register_code"
fi

# 2. تسجيل الدخول
login_response=$(curl -s -X POST "$API_BASE/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$TEST_USER\",\"password\":\"$TEST_PASSWORD\"}" \
    -w "\n%{http_code}")
login_code=$(echo "$login_response" | tail -1)
USER_TOKEN=$(echo "$login_response" | head -1 | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4 || echo "")

if [ "$login_code" = "200" ] && [ -n "$USER_TOKEN" ]; then
    log_test "2. تسجيل الدخول والحصول على token" "pass"
else
    log_test "2. تسجيل الدخول والحصول على token" "fail" "- كود: $login_code"
fi

# 3. إنشاء مساحة عمل
if [ -n "$USER_TOKEN" ]; then
    workspace_response=$(curl -s -X POST "$API_BASE/api/v1/workspaces" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"name":"مساحة عمل الاختبار","description":"مساحة عمل للاختبار"}' \
        -w "\n%{http_code}")
    workspace_code=$(echo "$workspace_response" | tail -1)
    WORKSPACE_ID=$(echo "$workspace_response" | head -1 | grep -o '"id":"[^"]*"' | cut -d'"' -f4 || echo "")
    
    if [ "$workspace_code" = "200" ] || [ "$workspace_code" = "201" ]; then
        log_test "3. إنشاء مساحة عمل" "pass" "- ID: $WORKSPACE_ID"
    else
        log_test "3. إنشاء مساحة عمل" "fail" "- كود: $workspace_code"
    fi
fi

# 4. إنشاء مهمة في مساحة العمل
if [ -n "$USER_TOKEN" ] && [ -n "$WORKSPACE_ID" ]; then
    task_response=$(curl -s -X POST "$API_BASE/api/v1/tasks" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"goal\":\"مهمة اختبار التكامل\",\"workspace_id\":\"$WORKSPACE_ID\",\"token_budget\":1000000}" \
        -w "\n%{http_code}")
    task_code=$(echo "$task_response" | tail -1)
    TASK_ID=$(echo "$task_response" | head -1 | grep -o '"id":"[^"]*"' | cut -d'"' -f4 || echo "")
    
    if [ "$task_code" = "200" ] || [ "$task_code" = "201" ]; then
        log_test "4. إنشاء مهمة في مساحة العمل" "pass" "- ID: $TASK_ID"
    else
        log_test "4. إنشاء مهمة في مساحة العمل" "fail" "- كود: $task_code"
    fi
fi

# 5. رفع ملف للمهمة
if [ -n "$USER_TOKEN" ] && [ -n "$TASK_ID" ]; then
    # إنشاء ملف اختبار
    echo "محتوى اختبار" > /tmp/test_file.txt
    
    upload_request_response=$(curl -s -X POST "$API_BASE/api/v1/uploads/request" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"filename\":\"test_file.txt\",\"content_type\":\"text/plain\",\"size\":100,\"task_id\":\"$TASK_ID\"}" \
        -w "\n%{http_code}")
    upload_code=$(echo "$upload_request_response" | tail -1)
    
    if [ "$upload_code" = "200" ] || [ "$upload_code" = "201" ]; then
        log_test "5. طلب رفع ملف للمهمة" "pass"
    else
        log_test "5. طلب رفع ملف للمهمة" "fail" "- كود: $upload_code"
    fi
fi

# 6. تحديث حالة المهمة
if [ -n "$USER_TOKEN" ] && [ -n "$TASK_ID" ]; then
    update_response=$(curl -s -X PUT "$API_BASE/api/v1/tasks/$TASK_ID" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"status":"running"}' \
        -w "\n%{http_code}")
    update_code=$(echo "$update_response" | tail -1)
    
    if [ "$update_code" = "200" ]; then
        log_test "6. تحديث حالة المهمة إلى running" "pass"
    else
        log_test "6. تحديث حالة المهمة إلى running" "fail" "- كود: $update_code"
    fi
fi

# 7. الحصول على أحداث المهمة
if [ -n "$USER_TOKEN" ] && [ -n "$TASK_ID" ]; then
    events_response=$(curl -s "$API_BASE/api/v1/tasks/$TASK_ID/events" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -w "\n%{http_code}")
    events_code=$(echo "$events_response" | tail -1)
    
    if [ "$events_code" = "200" ]; then
        log_test "7. الحصول على أحداث المهمة" "pass"
    else
        log_test "7. الحصول على أحداث المهمة" "fail" "- كود: $events_code"
    fi
fi

# 8. إلغاء المهمة
if [ -n "$USER_TOKEN" ] && [ -n "$TASK_ID" ]; then
    cancel_response=$(curl -s -X POST "$API_BASE/api/v1/tasks/$TASK_ID/cancel" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -w "\n%{http_code}")
    cancel_code=$(echo "$cancel_response" | tail -1)
    
    if [ "$cancel_code" = "200" ]; then
        log_test "8. إلغاء المهمة" "pass"
    else
        log_test "8. إلغاء المهمة" "fail" "- كود: $cancel_code"
    fi
fi

# ═══ سيناريو 2: اختبار الموصلات ═══
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔌 سيناريو 2: اختبار دورة حياة الموصل"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -n "$USER_TOKEN" ]; then
    # 9. إنشاء موصل Google
    connector_response=$(curl -s -X POST "$API_BASE/api/v1/connectors" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"type":"google","name":"Google Connector Test","config":{"api_key":"test_key"}}' \
        -w "\n%{http_code}")
    connector_code=$(echo "$connector_response" | tail -1)
    CONNECTOR_ID=$(echo "$connector_response" | head -1 | grep -o '"id":"[^"]*"' | cut -d'"' -f4 || echo "")
    
    if [ "$connector_code" = "200" ] || [ "$connector_code" = "201" ]; then
        log_test "9. إنشاء موصل Google" "pass" "- ID: $CONNECTOR_ID"
    else
        log_test "9. إنشاء موصل Google" "fail" "- كود: $connector_code"
    fi
    
    # 10. تحديث الموصل
    if [ -n "$CONNECTOR_ID" ]; then
        update_connector_response=$(curl -s -X PUT "$API_BASE/api/v1/connectors/$CONNECTOR_ID" \
            -H "Authorization: Bearer $USER_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{"name":"Google Connector Updated"}' \
            -w "\n%{http_code}")
        update_connector_code=$(echo "$update_connector_response" | tail -1)
        
        if [ "$update_connector_code" = "200" ]; then
            log_test "10. تحديث الموصل" "pass"
        else
            log_test "10. تحديث الموصل" "fail" "- كود: $update_connector_code"
        fi
    fi
    
    # 11. حذف الموصل
    if [ -n "$CONNECTOR_ID" ]; then
        delete_connector_response=$(curl -s -X DELETE "$API_BASE/api/v1/connectors/$CONNECTOR_ID" \
            -H "Authorization: Bearer $USER_TOKEN" \
            -w "\n%{http_code}")
        delete_connector_code=$(echo "$delete_connector_response" | tail -1)
        
        if [ "$delete_connector_code" = "200" ] || [ "$delete_connector_code" = "204" ]; then
            log_test "11. حذف الموصل" "pass"
        else
            log_test "11. حذف الموصل" "fail" "- كود: $delete_connector_code"
        fi
    fi
fi

# ═══ سيناريو 3: اختبار الإعدادات ═══
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  سيناريو 3: اختبار دورة حياة الإعدادات"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -n "$USER_TOKEN" ]; then
    # 12. حفظ إعداد
    save_setting_response=$(curl -s -X POST "$API_BASE/api/v1/settings" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"key":"test_integration_setting","value":"test_value"}' \
        -w "\n%{http_code}")
    save_setting_code=$(echo "$save_setting_response" | tail -1)
    
    if [ "$save_setting_code" = "200" ] || [ "$save_setting_code" = "201" ]; then
        log_test "12. حفظ إعداد جديد" "pass"
    else
        log_test "12. حفظ إعداد جديد" "fail" "- كود: $save_setting_code"
    fi
    
    # 13. قراءة الإعداد
    get_setting_response=$(curl -s "$API_BASE/api/v1/settings/test_integration_setting" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -w "\n%{http_code}")
    get_setting_code=$(echo "$get_setting_response" | tail -1)
    
    if [ "$get_setting_code" = "200" ]; then
        log_test "13. قراءة الإعداد" "pass"
    else
        log_test "13. قراءة الإعداد" "fail" "- كود: $get_setting_code"
    fi
    
    # 14. تحديث الإعداد
    update_setting_response=$(curl -s -X PUT "$API_BASE/api/v1/settings/test_integration_setting" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"value":"updated_value"}' \
        -w "\n%{http_code}")
    update_setting_code=$(echo "$update_setting_response" | tail -1)
    
    if [ "$update_setting_code" = "200" ]; then
        log_test "14. تحديث الإعداد" "pass"
    else
        log_test "14. تحديث الإعداد" "fail" "- كود: $update_setting_code"
    fi
    
    # 15. حذف الإعداد
    delete_setting_response=$(curl -s -X DELETE "$API_BASE/api/v1/settings/test_integration_setting" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -w "\n%{http_code}")
    delete_setting_code=$(echo "$delete_setting_response" | tail -1)
    
    if [ "$delete_setting_code" = "200" ] || [ "$delete_setting_code" = "204" ]; then
        log_test "15. حذف الإعداد" "pass"
    else
        log_test "15. حذف الإعداد" "fail" "- كود: $delete_setting_code"
    fi
fi

# ═══ سيناريو 4: التحقق من التكامل بين الخدمات ═══
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔗 سيناريو 4: التحقق من التكامل بين الخدمات"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 16. التحقق من اتصال API بـ PostgreSQL
if docker-compose exec -T postgres pg_isready > /dev/null 2>&1; then
    log_test "16. اتصال API بـ PostgreSQL" "pass"
else
    log_test "16. اتصال API بـ PostgreSQL" "fail"
fi

# 17. التحقق من اتصال API بـ Redis
if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
    log_test "17. اتصال API بـ Redis" "pass"
else
    log_test "17. اتصال API بـ Redis" "fail"
fi

# 18. التحقق من اتصال API بـ MinIO
if curl -s http://localhost:9000/minio/health/live > /dev/null 2>&1; then
    log_test "18. اتصال API بـ MinIO" "pass"
else
    log_test "18. اتصال API بـ MinIO" "fail"
fi

# 19. التحقق من اتصال Celery Worker بـ Redis
if docker-compose ps | grep -q "worker.*Up"; then
    log_test "19. اتصال Celery Worker بـ Redis" "pass"
else
    log_test "19. اتصال Celery Worker بـ Redis" "fail"
fi

# 20. التحقق من Flower Dashboard
if curl -s http://localhost:5555/ > /dev/null 2>&1; then
    log_test "20. Flower Dashboard متاح" "pass"
else
    log_test "20. Flower Dashboard متاح" "fail"
fi

# ═══ النتائج النهائية ═══
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "📊 ملخص اختبار التكامل:"
echo "   - إجمالي الاختبارات: $TOTAL_TESTS"
echo "   - نجح: $((TOTAL_TESTS - FAILED))"
echo "   - فشل: $FAILED"
echo "═══════════════════════════════════════════════════════════════════════════════"

if [ $FAILED -eq 0 ]; then
    echo "✅ نجحت جميع اختبارات التكامل!"
    exit 0
else
    echo "❌ فشل $FAILED من $TOTAL_TESTS اختبار"
    exit 1
fi
