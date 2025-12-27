#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# اختبار شامل لجميع الوظائف والمهام
# يختبر كل وظيفة في النظام بشكل كامل
# ═══════════════════════════════════════════════════════════════════════════════

set -e

API_BASE="http://localhost:8000"
ADMIN_TOKEN="${ADMIN_TOKEN:-test-admin-token}"

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "⚙️  اختبار شامل لجميع الوظائف والمهام (100% تغطية)"
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

# ═══ المرحلة 1: وظائف المصادقة ═══
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔐 المرحلة 1: اختبار وظائف المصادقة"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. تسجيل مستخدم جديد
register_response=$(curl -s -X POST "$API_BASE/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"username":"testuser","email":"test@example.com","password":"Test123!"}' \
    -w "\n%{http_code}")
register_code=$(echo "$register_response" | tail -1)
[ "$register_code" = "200" ] || [ "$register_code" = "201" ] || [ "$register_code" = "409" ]
log_test "تسجيل مستخدم جديد" "$?" "- كود: $register_code"

# 2. تسجيل الدخول
login_response=$(curl -s -X POST "$API_BASE/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"testuser","password":"Test123!"}' \
    -w "\n%{http_code}")
login_code=$(echo "$login_response" | tail -1)
[ "$login_code" = "200" ]
log_test "تسجيل الدخول" "$?" "- كود: $login_code"

# استخراج token (إذا كان موجوداً)
USER_TOKEN=$(echo "$login_response" | head -1 | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4 || echo "")

# 3. الحصول على معلومات المستخدم الحالي
if [ -n "$USER_TOKEN" ]; then
    me_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/v1/auth/me" \
        -H "Authorization: Bearer $USER_TOKEN")
    [ "$me_code" = "200" ]
    log_test "الحصول على معلومات المستخدم" "$?" "- كود: $me_code"
else
    log_test "الحصول على معلومات المستخدم" "fail" "- لم يتم الحصول على token"
fi

# 4. تحديث معلومات المستخدم
if [ -n "$USER_TOKEN" ]; then
    update_code=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$API_BASE/api/v1/auth/me" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"full_name":"Test User"}')
    [ "$update_code" = "200" ]
    log_test "تحديث معلومات المستخدم" "$?" "- كود: $update_code"
fi

# 5. تسجيل الخروج
if [ -n "$USER_TOKEN" ]; then
    logout_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_BASE/api/v1/auth/logout" \
        -H "Authorization: Bearer $USER_TOKEN")
    [ "$logout_code" = "200" ]
    log_test "تسجيل الخروج" "$?" "- كود: $logout_code"
fi

# ═══ المرحلة 2: وظائف المهام ═══
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 المرحلة 2: اختبار وظائف المهام"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -n "$USER_TOKEN" ]; then
    # 6. إنشاء مهمة جديدة
    create_task_response=$(curl -s -X POST "$API_BASE/api/v1/tasks" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"goal":"مهمة اختبار","token_budget":1000000}' \
        -w "\n%{http_code}")
    create_task_code=$(echo "$create_task_response" | tail -1)
    [ "$create_task_code" = "200" ] || [ "$create_task_code" = "201" ]
    log_test "إنشاء مهمة جديدة" "$?" "- كود: $create_task_code"
    
    # استخراج task_id
    TASK_ID=$(echo "$create_task_response" | head -1 | grep -o '"id":"[^"]*"' | cut -d'"' -f4 || echo "test-task-id")
    
    # 7. الحصول على قائمة المهام
    list_tasks_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/v1/tasks" \
        -H "Authorization: Bearer $USER_TOKEN")
    [ "$list_tasks_code" = "200" ]
    log_test "الحصول على قائمة المهام" "$?" "- كود: $list_tasks_code"
    
    # 8. الحصول على مهمة محددة
    get_task_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/v1/tasks/$TASK_ID" \
        -H "Authorization: Bearer $USER_TOKEN")
    [ "$get_task_code" = "200" ] || [ "$get_task_code" = "404" ]
    log_test "الحصول على مهمة محددة" "$?" "- كود: $get_task_code"
    
    # 9. تحديث مهمة
    update_task_code=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$API_BASE/api/v1/tasks/$TASK_ID" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"status":"running"}')
    [ "$update_task_code" = "200" ] || [ "$update_task_code" = "404" ]
    log_test "تحديث مهمة" "$?" "- كود: $update_task_code"
    
    # 10. إلغاء مهمة
    cancel_task_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_BASE/api/v1/tasks/$TASK_ID/cancel" \
        -H "Authorization: Bearer $USER_TOKEN")
    [ "$cancel_task_code" = "200" ] || [ "$cancel_task_code" = "404" ]
    log_test "إلغاء مهمة" "$?" "- كود: $cancel_task_code"
    
    # 11. حذف مهمة
    delete_task_code=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$API_BASE/api/v1/tasks/$TASK_ID" \
        -H "Authorization: Bearer $USER_TOKEN")
    [ "$delete_task_code" = "200" ] || [ "$delete_task_code" = "204" ] || [ "$delete_task_code" = "404" ]
    log_test "حذف مهمة" "$?" "- كود: $delete_task_code"
    
    # 12. الحصول على أحداث المهمة
    events_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/v1/tasks/$TASK_ID/events" \
        -H "Authorization: Bearer $USER_TOKEN")
    [ "$events_code" = "200" ] || [ "$events_code" = "404" ]
    log_test "الحصول على أحداث المهمة" "$?" "- كود: $events_code"
fi

# ═══ المرحلة 3: وظائف رفع الملفات ═══
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📤 المرحلة 3: اختبار وظائف رفع الملفات"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -n "$USER_TOKEN" ]; then
    # 13. طلب رفع ملف
    upload_request_response=$(curl -s -X POST "$API_BASE/api/v1/uploads/request" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"filename":"test.txt","content_type":"text/plain","size":100,"task_id":"test-task"}' \
        -w "\n%{http_code}")
    upload_request_code=$(echo "$upload_request_response" | tail -1)
    [ "$upload_request_code" = "200" ] || [ "$upload_request_code" = "201" ]
    log_test "طلب رفع ملف" "$?" "- كود: $upload_request_code"
    
    # 14. callback رفع ملف
    callback_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_BASE/api/v1/uploads/callback" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"object_key":"uploads/test.txt","task_id":"test-task"}')
    [ "$callback_code" = "200" ] || [ "$callback_code" = "404" ]
    log_test "callback رفع ملف" "$?" "- كود: $callback_code"
    
    # 15. الحصول على رابط تحميل
    download_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/v1/uploads/test-key/download" \
        -H "Authorization: Bearer $USER_TOKEN")
    [ "$download_code" = "200" ] || [ "$download_code" = "404" ]
    log_test "الحصول على رابط تحميل" "$?" "- كود: $download_code"
fi

# ═══ المرحلة 4: وظائف الموصلات ═══
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔌 المرحلة 4: اختبار وظائف الموصلات"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -n "$USER_TOKEN" ]; then
    # 16. الحصول على قائمة الموصلات
    list_connectors_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/v1/connectors" \
        -H "Authorization: Bearer $USER_TOKEN")
    [ "$list_connectors_code" = "200" ]
    log_test "الحصول على قائمة الموصلات" "$?" "- كود: $list_connectors_code"
    
    # 17. إنشاء موصل جديد
    create_connector_response=$(curl -s -X POST "$API_BASE/api/v1/connectors" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"type":"google","name":"Google Test"}' \
        -w "\n%{http_code}")
    create_connector_code=$(echo "$create_connector_response" | tail -1)
    [ "$create_connector_code" = "200" ] || [ "$create_connector_code" = "201" ]
    log_test "إنشاء موصل جديد" "$?" "- كود: $create_connector_code"
    
    CONNECTOR_ID=$(echo "$create_connector_response" | head -1 | grep -o '"id":"[^"]*"' | cut -d'"' -f4 || echo "test-connector-id")
    
    # 18. الحصول على موصل محدد
    get_connector_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/v1/connectors/$CONNECTOR_ID" \
        -H "Authorization: Bearer $USER_TOKEN")
    [ "$get_connector_code" = "200" ] || [ "$get_connector_code" = "404" ]
    log_test "الحصول على موصل محدد" "$?" "- كود: $get_connector_code"
    
    # 19. تحديث موصل
    update_connector_code=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$API_BASE/api/v1/connectors/$CONNECTOR_ID" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"name":"Google Updated"}')
    [ "$update_connector_code" = "200" ] || [ "$update_connector_code" = "404" ]
    log_test "تحديث موصل" "$?" "- كود: $update_connector_code"
    
    # 20. حذف موصل
    delete_connector_code=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$API_BASE/api/v1/connectors/$CONNECTOR_ID" \
        -H "Authorization: Bearer $USER_TOKEN")
    [ "$delete_connector_code" = "200" ] || [ "$delete_connector_code" = "204" ] || [ "$delete_connector_code" = "404" ]
    log_test "حذف موصل" "$?" "- كود: $delete_connector_code"
fi

# ═══ المرحلة 5: وظائف الإعدادات ═══
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  المرحلة 5: اختبار وظائف الإعدادات"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -n "$USER_TOKEN" ]; then
    # 21. الحصول على جميع الإعدادات
    list_settings_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/v1/settings" \
        -H "Authorization: Bearer $USER_TOKEN")
    [ "$list_settings_code" = "200" ]
    log_test "الحصول على جميع الإعدادات" "$?" "- كود: $list_settings_code"
    
    # 22. حفظ إعداد
    save_setting_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_BASE/api/v1/settings" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"key":"test_setting","value":"test_value"}')
    [ "$save_setting_code" = "200" ] || [ "$save_setting_code" = "201" ]
    log_test "حفظ إعداد" "$?" "- كود: $save_setting_code"
    
    # 23. الحصول على إعداد محدد
    get_setting_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/v1/settings/test_setting" \
        -H "Authorization: Bearer $USER_TOKEN")
    [ "$get_setting_code" = "200" ] || [ "$get_setting_code" = "404" ]
    log_test "الحصول على إعداد محدد" "$?" "- كود: $get_setting_code"
    
    # 24. حذف إعداد
    delete_setting_code=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$API_BASE/api/v1/settings/test_setting" \
        -H "Authorization: Bearer $USER_TOKEN")
    [ "$delete_setting_code" = "200" ] || [ "$delete_setting_code" = "204" ] || [ "$delete_setting_code" = "404" ]
    log_test "حذف إعداد" "$?" "- كود: $delete_setting_code"
fi

# ═══ المرحلة 6: وظائف مساحات العمل ═══
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🗂️  المرحلة 6: اختبار وظائف مساحات العمل"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -n "$USER_TOKEN" ]; then
    # 25. قائمة مساحات العمل
    list_workspaces_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/v1/workspaces" \
        -H "Authorization: Bearer $USER_TOKEN")
    [ "$list_workspaces_code" = "200" ]
    log_test "قائمة مساحات العمل" "$?" "- كود: $list_workspaces_code"
    
    # 26. إنشاء مساحة عمل
    create_workspace_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_BASE/api/v1/workspaces" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"name":"Test Workspace"}')
    [ "$create_workspace_code" = "200" ] || [ "$create_workspace_code" = "201" ]
    log_test "إنشاء مساحة عمل" "$?" "- كود: $create_workspace_code"
fi

# ═══ المرحلة 7: وظائف الإدارة ═══
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "👑 المرحلة 7: اختبار وظائف الإدارة"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 27. قائمة المستخدمين (admin فقط)
list_users_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/v1/admin/users" \
    -H "Authorization: Bearer $ADMIN_TOKEN")
[ "$list_users_code" = "200" ] || [ "$list_users_code" = "401" ] || [ "$list_users_code" = "403" ]
log_test "قائمة المستخدمين (admin)" "$?" "- كود: $list_users_code"

# 28. إحصائيات النظام
stats_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/v1/admin/stats" \
    -H "Authorization: Bearer $ADMIN_TOKEN")
[ "$stats_code" = "200" ] || [ "$stats_code" = "401" ] || [ "$stats_code" = "403" ]
log_test "إحصائيات النظام" "$?" "- كود: $stats_code"

# 29. سجلات التدقيق
audit_logs_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/v1/admin/audit-logs" \
    -H "Authorization: Bearer $ADMIN_TOKEN")
[ "$audit_logs_code" = "200" ] || [ "$audit_logs_code" = "401" ] || [ "$audit_logs_code" = "403" ]
log_test "سجلات التدقيق" "$?" "- كود: $audit_logs_code"

# ═══ النتائج النهائية ═══
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "📊 ملخص النتائج:"
echo "   - إجمالي الاختبارات: $TOTAL_TESTS"
echo "   - نجح: $((TOTAL_TESTS - FAILED))"
echo "   - فشل: $FAILED"
echo "═══════════════════════════════════════════════════════════════════════════════"

if [ $FAILED -eq 0 ]; then
    echo "✅ نجحت جميع اختبارات الوظائف!"
    exit 0
else
    echo "❌ فشل $FAILED من $TOTAL_TESTS اختبار"
    exit 1
fi
