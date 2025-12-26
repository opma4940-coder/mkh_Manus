#!/bin/bash
# =============================================================================
# mkh_Manus Smart Launcher (الـمُشغل الذكي)
# =============================================================================

set -e

# 1. تحديد مسار المشروع
if [ -z "$1" ]; then
    # إذا لم يتم توفير مسار، نستخدم المجلد الحالي
    PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    # إذا تم توفير مسار، ننتقل إليه
    PROJECT_ROOT="$1"
    cd "$PROJECT_ROOT" || { echo "❌ المسار غير صحيح!"; exit 1; }
fi

echo "🚀 جاري تشغيل mkh_Manus من: $PROJECT_ROOT"

# 2. التحقق من التثبيت (إذا لم يكن موجوداً، نقوم بالتثبيت)
if [ ! -d ".venv" ] || [ ! -d "manus_pro/frontend/node_modules" ]; then
    echo "📦 أول مرة تشغيل؟ جاري التثبيت التلقائي..."
    chmod +x setup_and_run.sh
    ./setup_and_run.sh
fi

source .venv/bin/activate

# 3. وظيفة لإغلاق العمليات عند الخروج
cleanup() {
    echo ""
    echo "🛑 جاري إيقاف mkh_Manus..."
    kill $BACKEND_PID $WORKER_PID $FRONTEND_PID 2>/dev/null || true
    exit
}
trap cleanup SIGINT SIGTERM

# 4. تشغيل Backend
echo "📡 تشغيل Backend API..."
PYTHONPATH=manus_pro/backend/src python -m manus_pro_server > /dev/null 2>&1 &
BACKEND_PID=$!

# 5. تشغيل Worker
echo "🤖 تشغيل Worker (Autonomous Runtime)..."
PYTHONPATH=manus_pro/backend/src python -m manus_pro_server.worker > /dev/null 2>&1 &
WORKER_PID=$!

# 6. تشغيل Frontend
echo "💻 تشغيل Dashboard..."
cd manus_pro/frontend
npm run dev -- --port 5173 > /dev/null 2>&1 &
FRONTEND_PID=$!
cd ../..

# 7. محاولة فتح المتصفح تلقائياً
echo "🌐 جاري فتح الداشبورد..."
sleep 5
URL="http://localhost:5173"

if command -v xdg-open > /dev/null; then
    xdg-open $URL
elif command -v open > /dev/null; then
    open $URL
elif command -v termux-open > /dev/null; then
    termux-open $URL
fi

echo ""
echo "✅ mkh_Manus يعمل الآن!"
echo "🔗 الرابط: $URL"
echo "⌨️ اضغط Ctrl+C لإيقاف النظام بالكامل."
echo ""

# الانتظار لإبقاء السكريبت يعمل
wait
