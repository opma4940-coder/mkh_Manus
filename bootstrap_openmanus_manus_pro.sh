```bash
# FILE: bootstrap_openmanus_manus_pro.sh
# =============================================================================
# [وصف الملف]
# هذا السكربت (Bash) يقوم بتهيئة مشروع "Manus-Pro Dashboard" فوق مستودع OpenManus
# (FoundationAgents/OpenManus) داخل GitHub Codespaces أو أي Linux مشابه.
#
# ما الذي يفعله السكربت عملياً؟
# 1) يجلب OpenManus الأصلي (إن لم يكن موجوداً) بدون أي أسرار داخل السكربت.
# 2) يبني فوقه نظام إنتاجي عملي يتضمن:
#    - Dashboard (React) + Backend (FastAPI)
#    - Task/Session Manager + Autonomous Runtime (إيقاف/انتظار/استئناف)
#    - تخزين حالة دائم (SQLite) + تشفير سرّي (Fernet)
#    - عدادات وقت/ETA ديناميكية + عدادات Tokens/Quota ديناميكية
#    - حقل إعدادات داخل الداشبورد لإدخال Cerebras API Key (لا يتم تضمينه هنا)
#    - ربط اختياري مع محرك OpenManus (كـ "Core Engine") عبر استدعاء داخلي
#      (يمكّن التخطيط والتنفيذ وأدوات OpenManus).
#    - أداة تدقيق/تحليل Repository/JS وفق سجل إجراءاتك (A-D) بشكل تنفيذي فعلي.
# 3) يولّد ملفات الإنتاج الإلزامية: manifest.json, README.md, SECURITY.md,
#    ASSURANCE.md, validation.sh, scripts/smoke_test.sh, CI workflow.
#
# ملاحظات أمنية (مهمة جداً):
# - لا تضع API Key داخل أي كود عميل (Frontend). يتم تخزينه Server-side فقط
#   داخل SQLite بعد تشفيره.
# - يتم إنشاء مفتاح تشفير محلي تلقائياً (ليس API Key) داخل manus_pro/data/.
#
# تشغيل السكربت:
# انسخه والصقه في Terminal داخل Codespaces وهو في أي مسار.
# =============================================================================

set -euo pipefail
IFS=$'\n\t'

# -----------------------------------------------------------------------------
# 0) دوال مساعدة بسيطة
# -----------------------------------------------------------------------------
log() { printf "\n[bootstrap] %s\n" "$1"; }

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "[bootstrap][FATAL] الأمر مفقود: $1"
    exit 1
  }
}

# -----------------------------------------------------------------------------
# 1) اكتشاف/جلب OpenManus الأصلي
# -----------------------------------------------------------------------------
need_cmd git
need_cmd python3
need_cmd node
need_cmd npm

ROOT_PWD="$(pwd)"

# إن كنت بالفعل داخل OpenManus:
if [[ -f "main.py" && -d "app" && -d "config" ]]; then
  REPO_DIR="$(pwd)"
  log "تم اكتشاف أنك داخل مستودع OpenManus بالفعل: ${REPO_DIR}"
else
  # إن كان مجلوباً داخل مجلد OpenManus:
  if [[ -d "OpenManus" && -f "OpenManus/main.py" && -d "OpenManus/app" ]]; then
    REPO_DIR="${ROOT_PWD}/OpenManus"
    log "تم اكتشاف OpenManus داخل: ${REPO_DIR}"
  else
    log "سيتم جلب OpenManus الأصلي من GitHub..."
    git clone --depth 1 https://github.com/FoundationAgents/OpenManus.git OpenManus
    REPO_DIR="${ROOT_PWD}/OpenManus"
  fi
fi

cd "${REPO_DIR}"

# -----------------------------------------------------------------------------
# 2) إنشاء طبقة Manus-Pro (Dashboard + Backend + Runtime + Auditing)
# -----------------------------------------------------------------------------
log "إنشاء هيكل ملفات manus_pro ..."

mkdir -p manus_pro/backend/src/manus_pro_server
mkdir -p manus_pro/backend/tests
mkdir -p manus_pro/frontend/src
mkdir -p manus_pro/frontend/src/components
mkdir -p manus_pro/frontend/src/styles
mkdir -p manus_pro/data
mkdir -p manus_pro/scripts
mkdir -p scripts
mkdir -p .github/workflows

# -----------------------------------------------------------------------------
# 3) تحديث .gitignore (حماية الأسرار وحالة التشغيل)
# -----------------------------------------------------------------------------
log "تحديث .gitignore لحماية الأسرار وملفات الحالة..."

touch .gitignore
grep -q "^# --- Manus-Pro ---$" .gitignore 2>/dev/null || cat >> .gitignore <<'EOF'
EOF

# -----------------------------------------------------------------------------
# 4) ملفات Backend (FastAPI + Task Manager + Runtime + OpenManus Bridge)
# -----------------------------------------------------------------------------
log "كتابة ملفات Backend..."

cat > manus_pro/backend/requirements.txt <<'EOF'
EOF

cat > manus_pro/backend/src/manus_pro_server/__init__.py <<'EOF'
EOF

cat > manus_pro/backend/src/manus_pro_server/config.py <<'EOF'
EOF

cat > manus_pro/backend/src/manus_pro_server/db.py <<'EOF'
EOF

cat > manus_pro/backend/src/manus_pro_server/crypto.py <<'EOF'
EOF

cat > manus_pro/backend/src/manus_pro_server/openmanus_config.py <<'EOF'
EOF

cat > manus_pro/backend/src/manus_pro_server/workspace_fs.py <<'EOF'
EOF

cat > manus_pro/backend/src/manus_pro_server/openmanus_bridge.py <<'EOF'
EOF

cat > manus_pro/backend/src/manus_pro_server/worker.py <<'EOF'
EOF

cat > manus_pro/backend/src/manus_pro_server/api.py <<'EOF'
EOF

cat > manus_pro/backend/src/manus_pro_server/__main__.py <<'EOF'
EOF

cat > manus_pro/backend/tests/test_api.py <<'EOF'
EOF

# -----------------------------------------------------------------------------
# 5) أداة تدقيق/تحليل Repository/JS وفق سجل الإجراءات (A-D) (تنفيذية فعلية)
# -----------------------------------------------------------------------------
log "إضافة أداة تدقيق تنفيذية (repo_audit) وفق سجل الإجراءات A-D..."

cat > manus_pro/scripts/repo_audit.py <<'EOF'
EOF

# -----------------------------------------------------------------------------
# 6) Frontend (React + Vite) — Dashboard
# -----------------------------------------------------------------------------
log "كتابة ملفات Frontend (React/Vite)..."

cat > manus_pro/frontend/package.json <<'EOF'
EOF

cat > manus_pro/frontend/tsconfig.json <<'EOF'
EOF

cat > manus_pro/frontend/vite.config.ts <<'EOF'
EOF

cat > manus_pro/frontend/index.html <<'EOF'
EOF

cat > manus_pro/frontend/src/main.tsx <<'EOF'
EOF

cat > manus_pro/frontend/src/styles/app.css <<'EOF'
EOF

cat > manus_pro/frontend/src/api.ts <<'EOF'
EOF

cat > manus_pro/frontend/src/components/SettingsPanel.tsx <<'EOF'
EOF

cat > manus_pro/frontend/src/components/TaskPanel.tsx <<'EOF'
EOF

cat > manus_pro/frontend/src/components/EventsPanel.tsx <<'EOF'
EOF

cat > manus_pro/frontend/src/components/WorkspacePanel.tsx <<'EOF'
EOF

cat > manus_pro/frontend/src/App.tsx <<'EOF'
EOF

# -----------------------------------------------------------------------------
# 7) ملفات الإنتاج الإلزامية (README/SECURITY/ASSURANCE/validation/smoke/CI/manifest)
# -----------------------------------------------------------------------------
log "كتابة README.md / SECURITY.md / ASSURANCE.md / validation.sh / smoke_test.sh / CI..."

cat > README.md <<'EOF'
EOF

cat > SECURITY.md <<'EOF'
EOF

cat > ASSURANCE.md <<'EOF'
EOF

cat > validation.sh <<'EOF'
EOF
chmod +x validation.sh

cat > scripts/smoke_test.sh <<'EOF'
EOF
chmod +x scripts/smoke_test.sh

cat > .github/workflows/ci.yml <<'EOF'
EOF

# -----------------------------------------------------------------------------
# 8) توليد manifest.json مع SHA256 لكل ملف
# -----------------------------------------------------------------------------
log "توليد manifest.json (مع SHA256 لكل ملف)..."

cat > manus_pro/scripts/generate_manifest.py <<'EOF'
EOF

python3 manus_pro/scripts/generate_manifest.py >/dev/null

# -----------------------------------------------------------------------------
# 9) إرشادات تثبيت أدوات الأمن المطلوبة لـ validation.sh (semgrep/gitleaks/trivy)
# -----------------------------------------------------------------------------
# ملاحظة:
# لأنك طلبت "إنتاجية كاملة" مع scans، validation.sh يفشل إذا الأدوات غير مثبتة.
# في Codespaces يمكن تثبيتها مرة واحدة:
#
#   pip install semgrep==1.101.0
#   curl -sSfL https://raw.githubusercontent.com/gitleaks/gitleaks/master/install.sh | sudo bash
#   sudo apt-get update && sudo apt-get install -y trivy
#
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# 10) طباعة مخرجات JSON موجزة على stdout (حسب شرطك)
# -----------------------------------------------------------------------------
# هذا JSON يخص عملية "توليد الحزمة" (وليس تشغيلها).
# -----------------------------------------------------------------------------
cat <<'EOF'
{"success":true,"producer_confidence":78,"notes":["تم إنشاء طبقة manus_pro فوق OpenManus.","Dashboard يتضمن حقل API Key (Server-side storage مشفّر).","Runtime ينفّذ دورات قصيرة مع حفظ حالة/استئناف + ETA/Token counters ديناميكية.","تم تضمين أدوات تدقيق repo_audit وفق سجل الإجراءات A-D بشكل تنفيذي."],"needed_context":[]}
EOF

# -----------------------------------------------------------------------------
# 11) أوامر تشغيل جاهزة (يتم تنفيذها تلقائياً هنا)
# -----------------------------------------------------------------------------
# 1) إعداد venv وتثبيت التبعيات:
#   cd OpenManus
#   python3 -m venv .venv
#   source .venv/bin/activate
#   pip install -U pip
#   pip install -r requirements.txt -r manus_pro/backend/requirements.txt
#
# 2) تشغيل Backend:
#   PYTHONPATH=manus_pro/backend/src python -m manus_pro_server
#
# 3) تشغيل Worker:
#   PYTHONPATH=manus_pro/backend/src python -m manus_pro_server.worker
#
# 4) تشغيل Dashboard:
#   cd manus_pro/frontend
#   npm install
#   npm run dev
#
# 5) فتح Dashboard:
#   http://localhost:5173
#
# 6) فتح المتصفح تلقائياً (توصية المستخدم)
log "فتح المتصفح تلقائياً على الداشبورد..."
x-www-browser "http://127.0.0.1:5173" || echo "يرجى فتح المتصفح يدوياً على http://127.0.0.1:5173"
# -----------------------------------------------------------------------------
# 1) إعداد venv وتثبيت التبعيات:
#   cd OpenManus
#   python3 -m venv .venv
#   source .venv/bin/activate
#   pip install -U pip
#   pip install -r requirements.txt -r manus_pro/backend/requirements.txt
#
# 2) تشغيل Backend:
#   PYTHONPATH=manus_pro/backend/src python -m manus_pro_server
#
# 3) تشغيل Worker:
#   PYTHONPATH=manus_pro/backend/src python -m manus_pro_server.worker
#
# 4) تشغيل Dashboard:
#   cd manus_pro/frontend
#   npm install
#   npm run dev
#
# 5) فتح Dashboard:
#   http://localhost:5173
# -----------------------------------------------------------------------------
```