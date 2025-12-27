# --- المرحلة 1: بناء Frontend ---
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

# نسخ ملفات التبعيات من المسار الجديد
COPY frontend/package.json frontend/pnpm-lock.yaml* ./
RUN npm install -g pnpm && pnpm install

# نسخ كود الواجهة من المسار الجديد
COPY frontend/ ./
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

# نسخ الملفات بالمسارات الجديدة الموحدة
COPY run_server.py /app/
COPY backend /app/backend
COPY frontend /app/frontend
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend/app:/app/backend/src/manus_pro_server:${PYTHONPATH}
ENV PORT=8000

# نسخ entrypoint script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
