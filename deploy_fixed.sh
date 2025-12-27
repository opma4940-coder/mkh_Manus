#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# سكريبت النشر المحسّن لنظام mkh_Manus
# يتضمن: تثبيت Docker، بناء الصور، تشغيل الخدمات، التحقق من الصحة
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# الألوان
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🚀 بدء عملية نشر نظام mkh_Manus${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# التحقق من وجود Docker
echo -e "${YELLOW}🔍 التحقق من Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker غير مثبت${NC}"
    echo -e "${YELLOW}📦 تثبيت Docker...${NC}"
    
    # تثبيت Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    
    echo -e "${GREEN}✅ تم تثبيت Docker بنجاح${NC}"
    echo -e "${YELLOW}⚠️  يرجى تسجيل الخروج والدخول مرة أخرى لتفعيل صلاحيات Docker${NC}"
    echo -e "${YELLOW}⚠️  ثم قم بتشغيل هذا السكريبت مرة أخرى${NC}"
    exit 0
else
    echo -e "${GREEN}✅ Docker مثبت بالفعل${NC}"
fi

# التحقق من وجود Docker Compose
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose غير متاح${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker Compose متاح${NC}"
echo ""

# التحقق من ملف .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  ملف .env غير موجود، نسخ من .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ تم إنشاء ملف .env${NC}"
fi

# إيقاف الخدمات القديمة
echo -e "${YELLOW}🛑 إيقاف الخدمات القديمة...${NC}"
docker compose down -v 2>/dev/null || true
echo ""

# بناء الصور
echo -e "${YELLOW}🔨 بناء صور Docker...${NC}"
docker compose build --no-cache
echo -e "${GREEN}✅ تم بناء الصور بنجاح${NC}"
echo ""

# تشغيل قاعدة البيانات أولاً
echo -e "${YELLOW}🗄️  تشغيل قاعدة البيانات PostgreSQL...${NC}"
docker compose up -d postgres
echo ""

# انتظار جاهزية قاعدة البيانات
echo -e "${YELLOW}⏳ انتظار جاهزية قاعدة البيانات...${NC}"
sleep 10

# التحقق من صحة قاعدة البيانات
if docker compose exec -T postgres pg_isready -U mkh_user -d mkh_manus &> /dev/null; then
    echo -e "${GREEN}✅ قاعدة البيانات جاهزة${NC}"
else
    echo -e "${RED}❌ فشل تشغيل قاعدة البيانات${NC}"
    docker compose logs postgres
    exit 1
fi
echo ""

# تطبيق migrations
echo -e "${YELLOW}📊 تطبيق migrations على قاعدة البيانات...${NC}"
if [ -f migrations/init.sql ]; then
    docker compose exec -T postgres psql -U mkh_user -d mkh_manus < migrations/init.sql
    echo -e "${GREEN}✅ تم تطبيق migrations بنجاح${NC}"
else
    echo -e "${YELLOW}⚠️  ملف migrations/init.sql غير موجود، تخطي...${NC}"
fi
echo ""

# تشغيل Redis و MinIO
echo -e "${YELLOW}🔴 تشغيل Redis و MinIO...${NC}"
docker compose up -d redis minio
echo ""

# انتظار جاهزية الخدمات
echo -e "${YELLOW}⏳ انتظار جاهزية الخدمات...${NC}"
sleep 10
echo ""

# تشغيل جميع الخدمات
echo -e "${YELLOW}🚀 تشغيل جميع الخدمات...${NC}"
docker compose up -d
echo ""

# انتظار بدء الخدمات
echo -e "${YELLOW}⏳ انتظار بدء الخدمات (60 ثانية)...${NC}"
sleep 60
echo ""

# التحقق من حالة الخدمات
echo -e "${YELLOW}🔍 التحقق من حالة الخدمات...${NC}"
docker compose ps
echo ""

# التحقق من صحة API
echo -e "${YELLOW}🏥 فحص صحة API...${NC}"
if curl -f http://localhost:8000/api/v1/health &> /dev/null; then
    echo -e "${GREEN}✅ API يعمل بنجاح!${NC}"
else
    echo -e "${RED}❌ فشل فحص صحة API${NC}"
    echo -e "${YELLOW}📋 عرض سجلات API:${NC}"
    docker compose logs --tail=50 api
    exit 1
fi
echo ""

# عرض معلومات الوصول
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ تم نشر النظام بنجاح!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}📍 روابط الوصول:${NC}"
echo -e "   ${BLUE}API:${NC}     http://localhost:8000"
echo -e "   ${BLUE}Health:${NC}  http://localhost:8000/api/v1/health"
echo -e "   ${BLUE}Flower:${NC}  http://localhost:5555"
echo -e "   ${BLUE}MinIO:${NC}   http://localhost:9001"
echo ""
echo -e "${YELLOW}📋 أوامر مفيدة:${NC}"
echo -e "   عرض السجلات:     ${BLUE}docker compose logs -f${NC}"
echo -e "   إيقاف الخدمات:   ${BLUE}docker compose down${NC}"
echo -e "   إعادة التشغيل:   ${BLUE}docker compose restart${NC}"
echo -e "   حالة الخدمات:    ${BLUE}docker compose ps${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
