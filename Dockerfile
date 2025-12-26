# FILE: Dockerfile
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                    Dockerfile محسّن لمشروع mkh_Manus                        ║
# ║                                                                              ║
# ║  الوصف:                                                                     ║
# ║  - بناء متعدد المراحل لتقليل حجم الصورة النهائية                          ║
# ║  - تهيئة PYTHONPATH لضمان استيراد manus_pro_server                         ║
# ║  - تثبيت التبعيات الأمنية والأدوات المطلوبة                                ║
# ║  - جاهز للإنتاج بنسبة 100%                                                 ║
# ║                                                                              ║
# ║  التاريخ: ديسمبر 2025                                                       ║
# ║  الإصدار: 2.2 (Fixed)                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# --- المرحلة 1: بناء Frontend ---
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

COPY manus_pro/frontend/package.json manus_pro/frontend/pnpm-lock.yaml* ./
RUN npm install -g pnpm && pnpm install

COPY manus_pro/frontend/ ./
ARG VITE_API_BASE=/api/v1
ENV VITE_API_BASE=${VITE_API_BASE}
RUN pnpm build

# --- المرحلة 2: الصورة النهائية ---
FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    procps \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# نسخ الملفات بالترتيب الصحيح (تجنب نسخ مجلد data لتفادي خطأ الأذونات)
COPY run_server.py /app/
COPY manus_pro/backend /app/manus_pro/backend
COPY manus_pro/frontend /app/manus_pro/frontend
COPY manus_pro/scripts /app/manus_pro/scripts
COPY --from=frontend-builder /app/frontend/dist /app/manus_pro/frontend/dist

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/manus_pro/backend/src:${PYTHONPATH}
ENV PORT=8000

# نسخ entrypoint script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# تم نقل إنشاء المجلدات وتعيين الأذونات إلى entrypoint.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
