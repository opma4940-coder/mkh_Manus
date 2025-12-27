# دليل النشر والاستكمال - نظام mkh_Manus

## 📋 ملخص المشكلة والحل

### المشكلة الأصلية
كانت حاوية `mkh_manus_api` تفشل في فحص الصحة (health check) بسبب عدم تطابق المسارات بين الملفات المختلفة.

### الحل المطبق
تم إصلاح جميع المسارات في الملفات التالية:
- ✅ `docker-compose.yml` - تصحيح مسارات volumes و PYTHONPATH
- ✅ `run_server.py` - تصحيح مسار backend/src
- ✅ `docker-entrypoint.sh` - تصحيح مسارات التحقق
- ✅ `config.py` - تصحيح مسارات DATA_DIR
- ✅ `api.py` - تصحيح مسار frontend/dist

### التغييرات الرئيسية

#### قبل الإصلاح:
```
./manus_pro/backend/src  ← مسار خاطئ
./manus_pro/data         ← مسار خاطئ
```

#### بعد الإصلاح:
```
./backend/src  ← مسار صحيح
./data         ← مسار صحيح
```

---

## 🚀 خطوات النشر

### الطريقة 1: استخدام السكريبت المحسّن (موصى به)

```bash
cd /home/ubuntu/mkh_Manus
./deploy_fixed.sh
```

هذا السكريبت يقوم بـ:
1. ✅ التحقق من تثبيت Docker
2. ✅ بناء الصور بدون cache
3. ✅ تشغيل قاعدة البيانات والتحقق من جاهزيتها
4. ✅ تطبيق migrations
5. ✅ تشغيل جميع الخدمات
6. ✅ فحص صحة API
7. ✅ عرض معلومات الوصول

### الطريقة 2: خطوات يدوية

```bash
# 1. إيقاف الخدمات القديمة
docker compose down -v

# 2. بناء الصور
docker compose build --no-cache

# 3. تشغيل قاعدة البيانات
docker compose up -d postgres
sleep 10

# 4. تطبيق migrations
docker compose exec -T postgres psql -U mkh_user -d mkh_manus < migrations/init.sql

# 5. تشغيل جميع الخدمات
docker compose up -d

# 6. انتظار بدء الخدمات
sleep 60

# 7. التحقق من الصحة
curl http://localhost:8000/api/v1/health
```

---

## 🔍 التحقق من النجاح

### 1. فحص حالة الحاويات
```bash
docker compose ps
```

يجب أن تكون جميع الحاويات في حالة `healthy` أو `running`:
- ✅ mkh_postgres (healthy)
- ✅ mkh_redis (healthy)
- ✅ mkh_minio (healthy)
- ✅ mkh_manus_api (healthy)
- ✅ mkh_celery_worker (running)
- ✅ mkh_celery_beat (running)
- ✅ mkh_flower (running)

### 2. فحص صحة API
```bash
curl http://localhost:8000/api/v1/health
```

يجب أن تحصل على:
```json
{"status":"ok","timestamp":1735286400.123}
```

### 3. فحص السجلات
```bash
# سجلات API
docker compose logs api

# سجلات جميع الخدمات
docker compose logs -f
```

---

## 🐛 استكشاف الأخطاء

### إذا فشلت حاوية API

#### 1. فحص السجلات
```bash
docker compose logs api --tail=100
```

#### 2. التحقق من المسارات داخل الحاوية
```bash
docker compose exec api ls -la /app/
docker compose exec api ls -la /app/backend/src/
docker compose exec api ls -la /app/backend/src/manus_pro_server/
```

#### 3. اختبار استيراد Python
```bash
docker compose exec api python3 -c "import sys; sys.path.insert(0, '/app/backend/src'); from manus_pro_server.api import app; print('Import successful!')"
```

#### 4. اختبار health endpoint يدوياً
```bash
docker compose exec api curl -f http://localhost:8000/api/v1/health
```

### إذا فشلت قاعدة البيانات

```bash
# فحص سجلات PostgreSQL
docker compose logs postgres

# التحقق من الاتصال
docker compose exec postgres pg_isready -U mkh_user -d mkh_manus

# الدخول إلى قاعدة البيانات
docker compose exec postgres psql -U mkh_user -d mkh_manus
```

### إذا فشل Redis

```bash
# فحص سجلات Redis
docker compose logs redis

# اختبار الاتصال
docker compose exec redis redis-cli ping
```

---

## 📊 معلومات الوصول

### الخدمات الرئيسية
- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/v1/health
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:8000

### أدوات المراقبة
- **Flower** (Celery Monitoring): http://localhost:5555
  - Username: `admin`
  - Password: `flower_admin_2025`

- **MinIO Console**: http://localhost:9001
  - Username: `mkh_minio_admin`
  - Password: `mkh_minio_secure_2025`

### قواعد البيانات
- **PostgreSQL**: localhost:5432
  - Database: `mkh_manus`
  - Username: `mkh_user`
  - Password: `mkh_secure_password_2025`

- **Redis**: localhost:6379
  - Password: `mkh_redis_pass_2025`

---

## 🔧 أوامر مفيدة

### إدارة الخدمات
```bash
# إيقاف جميع الخدمات
docker compose down

# إيقاف وحذف البيانات
docker compose down -v

# إعادة تشغيل خدمة معينة
docker compose restart api

# إعادة بناء وتشغيل
docker compose up -d --build

# عرض استخدام الموارد
docker stats
```

### السجلات
```bash
# سجلات جميع الخدمات
docker compose logs -f

# سجلات خدمة معينة
docker compose logs -f api

# آخر 100 سطر
docker compose logs --tail=100 api
```

### الصيانة
```bash
# تنظيف الصور غير المستخدمة
docker system prune -a

# تنظيف volumes غير المستخدمة
docker volume prune

# عرض حجم الاستخدام
docker system df
```

---

## 📝 ملاحظات مهمة

1. **المسارات الصحيحة**: تأكد من استخدام المسارات الجديدة في أي تعديلات مستقبلية:
   - `./backend/src` بدلاً من `./manus_pro/backend/src`
   - `./data` بدلاً من `./manus_pro/data`

2. **ملف .env**: تأكد من وجود ملف `.env` مع جميع المتغيرات المطلوبة

3. **الأمان**: غيّر كلمات المرور الافتراضية في الإنتاج

4. **النسخ الاحتياطي**: قم بعمل نسخ احتياطي لمجلد `data` بانتظام

---

## ✅ قائمة التحقق النهائية

- [ ] تم استنساخ المشروع من GitHub
- [ ] تم إنشاء ملف `.env` من `.env.example`
- [ ] تم تثبيت Docker و Docker Compose
- [ ] تم تشغيل سكريبت النشر `./deploy_fixed.sh`
- [ ] جميع الحاويات تعمل بنجاح
- [ ] API يستجيب على `/api/v1/health`
- [ ] يمكن الوصول إلى Frontend على `http://localhost:8000`
- [ ] Flower يعمل على `http://localhost:5555`
- [ ] MinIO يعمل على `http://localhost:9001`

---

## 📞 الدعم

إذا واجهت أي مشاكل:
1. راجع قسم "استكشاف الأخطاء" أعلاه
2. افحص السجلات باستخدام `docker compose logs`
3. تحقق من أن جميع المسارات صحيحة
4. تأكد من أن Docker يعمل بشكل صحيح

---

**تاريخ آخر تحديث**: 27 ديسمبر 2025  
**الإصدار**: 2.0 (بعد إصلاح المسارات)
