# FILE: scripts/smoke_test.sh
# =============================================================================
# [وصف الملف]
# Smoke Test بسيط وقابل للتشغيل دون الحاجة لتشغيل الخدمات:
# - يتحقق من وجود الملفات الأساسية
# - يتحقق من أن مسارات Manus-Pro موجودة
#
# ملاحظة:
# Smoke الحقيقي (HTTP) يُفضّل تشغيله عبر curl بعد تشغيل API/worker.
# =============================================================================

set -euo pipefail
IFS=$'\n\t'

test -f "README.md"
test -f "SECURITY.md"
test -f "ASSURANCE.md"
test -f "validation.sh"

test -d "manus_pro/backend/src/manus_pro_server"
test -d "manus_pro/frontend/src"

echo "[smoke] basic files OK"
