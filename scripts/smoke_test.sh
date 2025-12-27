#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# سكريبت اختبارات الدخان (Smoke Tests)
# يقوم بفحص جميع endpoints الأساسية للتأكد من عمل النظام
# ═══════════════════════════════════════════════════════════════════════════════

set -e

API_BASE="${API_BASE:-http://localhost:8000}"
FAILED=0

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🧪 بدء اختبارات الدخان (Smoke Tests)"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "🌐 API Base URL: $API_BASE"
echo ""

# دالة للاختبار
test_endpoint() {
    local name="$1"
    local url="$2"
    local method="${3:-GET}"
    local data="$4"
    
    echo -n "🔍 اختبار: $name ... "
    
    if [ "$method" = "GET" ]; then
        if curl -sf "$url" > /dev/null; then
            echo "✅ نجح"
            return 0
        else
            echo "❌ فشل"
            FAILED=$((FAILED + 1))
            return 1
        fi
    elif [ "$method" = "POST" ]; then
        if curl -sf -X POST -H "Content-Type: application/json" -d "$data" "$url" > /dev/null; then
            echo "✅ نجح"
            return 0
        else
            echo "❌ فشل"
            FAILED=$((FAILED + 1))
            return 1
        fi
    fi
}

# اختبار 1: Health Check
test_endpoint "Health Check" "$API_BASE/api/v1/health"

# اختبار 2: API Documentation
test_endpoint "API Docs" "$API_BASE/docs"

# اختبار 3: OpenAPI Schema
test_endpoint "OpenAPI Schema" "$API_BASE/openapi.json"

# اختبار 4: Upload Request
echo -n "🔍 اختبار: Upload Request ... "
UPLOAD_RESPONSE=$(curl -sf -X POST \
    -H "Content-Type: application/json" \
    -d '{"filename":"test.txt","content_type":"text/plain","size":100}' \
    "$API_BASE/api/v1/uploads/request" 2>/dev/null || echo "")

if [ -n "$UPLOAD_RESPONSE" ]; then
    if echo "$UPLOAD_RESPONSE" | grep -q "upload_url"; then
        echo "✅ نجح"
    else
        echo "❌ فشل (استجابة غير صحيحة)"
        FAILED=$((FAILED + 1))
    fi
else
    echo "❌ فشل (لا توجد استجابة)"
    FAILED=$((FAILED + 1))
fi

# اختبار 5: MinIO Health
echo -n "🔍 اختبار: MinIO Health ... "
if curl -sf "http://localhost:9000/minio/health/live" > /dev/null 2>&1; then
    echo "✅ نجح"
else
    echo "⚠️  تحذير (MinIO قد لا يكون متاحاً)"
fi

# اختبار 6: Redis Connection
echo -n "🔍 اختبار: Redis Connection ... "
if docker exec mkh_redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ نجح"
else
    echo "⚠️  تحذير (Redis قد لا يكون متاحاً)"
fi

# اختبار 7: PostgreSQL Connection
echo -n "🔍 اختبار: PostgreSQL Connection ... "
if docker exec mkh_postgres pg_isready -U mkh_user > /dev/null 2>&1; then
    echo "✅ نجح"
else
    echo "⚠️  تحذير (PostgreSQL قد لا يكون متاحاً)"
fi

# النتائج النهائية
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
if [ $FAILED -eq 0 ]; then
    echo "✅ جميع الاختبارات نجحت!"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    exit 0
else
    echo "❌ فشل $FAILED اختبار(ات)"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    exit 1
fi
