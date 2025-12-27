# ✅ ضمان الجودة والفحوصات - mkh_Manus

<div dir="rtl">

## نظرة عامة

يوفر هذا المستند قائمة شاملة بجميع الأدوات والفحوصات المطلوبة لضمان جودة وأمان نظام **mkh_Manus**. يجب تشغيل هذه الفحوصات بانتظام قبل كل إصدار وفي CI/CD pipeline.

---

## 🔍 فحوصات الكود

### 1. Linting (فحص جودة الكود)

#### Python (Flake8)

```bash
# تثبيت Flake8
pip install flake8

# تشغيل الفحص
flake8 backend/ --max-line-length=120 --ignore=E203,W503

# تشغيل مع تقرير HTML
flake8 backend/ --format=html --htmldir=reports/flake8
```

**التكوين**: يمكن إضافة ملف `.flake8` في جذر المشروع:
```ini
[flake8]
max-line-length = 120
ignore = E203, W503
exclude = .git,__pycache__,venv,migrations
```

#### JavaScript/TypeScript (ESLint)

```bash
# الانتقال إلى مجلد Frontend
cd frontend

# تشغيل الفحص
pnpm run lint

# إصلاح المشاكل تلقائياً
pnpm run lint:fix
```

---

### 2. Code Formatting (تنسيق الكود)

#### Python (Black)

```bash
# تثبيت Black
pip install black

# فحص التنسيق
black --check backend/

# تطبيق التنسيق
black backend/
```

#### JavaScript/TypeScript (Prettier)

```bash
cd frontend

# فحص التنسيق
pnpm run format:check

# تطبيق التنسيق
pnpm run format
```

---

### 3. Type Checking (فحص الأنواع)

#### Python (MyPy)

```bash
# تثبيت MyPy
pip install mypy

# تشغيل الفحص
mypy backend/ --ignore-missing-imports
```

#### TypeScript

```bash
cd frontend

# تشغيل فحص الأنواع
pnpm run type-check
```

---

## 🧪 الاختبارات

### 1. Unit Tests (اختبارات الوحدة)

#### Backend (Pytest)

```bash
# تثبيت Pytest
pip install pytest pytest-cov pytest-asyncio

# تشغيل جميع الاختبارات
pytest backend/tests/ -v

# تشغيل مع تقرير التغطية
pytest backend/tests/ --cov=backend --cov-report=html --cov-report=term

# تشغيل اختبارات محددة
pytest backend/tests/test_uploads.py -v
```

#### Frontend (Vitest)

```bash
cd frontend

# تشغيل الاختبارات
pnpm run test

# تشغيل مع التغطية
pnpm run test:coverage
```

---

### 2. Integration Tests (اختبارات التكامل)

```bash
# تشغيل اختبارات التكامل مع Docker
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# تشغيل اختبارات API
pytest backend/tests/integration/ -v
```

---

### 3. Smoke Tests (اختبارات الدخان)

```bash
# تشغيل اختبارات سريعة بعد النشر
./scripts/smoke_test.sh

# أو يدوياً:
curl -f http://localhost:8000/api/v1/health || exit 1
curl -f http://localhost:8000/docs || exit 1
```

---

## 🔒 الفحوصات الأمنية

### 1. Dependency Scanning (فحص التبعيات)

#### Python (Safety)

```bash
# تثبيت Safety
pip install safety

# فحص التبعيات
safety check --file requirements.txt

# فحص مع تقرير JSON
safety check --file requirements.txt --json > reports/safety.json
```

#### Node.js (pnpm audit)

```bash
cd frontend

# فحص التبعيات
pnpm audit

# فحص مع تقرير JSON
pnpm audit --json > ../reports/npm-audit.json
```

---

### 2. Secret Scanning (فحص الأسرار)

#### Detect-Secrets

```bash
# تثبيت detect-secrets
pip install detect-secrets

# فحص الأسرار
detect-secrets scan --all-files

# إنشاء baseline
detect-secrets scan > .secrets.baseline

# فحص مقابل baseline
detect-secrets audit .secrets.baseline
```

#### Gitleaks

```bash
# تثبيت Gitleaks
brew install gitleaks  # macOS
# أو تحميل من: https://github.com/gitleaks/gitleaks

# فحص المستودع
gitleaks detect --source . --verbose

# فحص مع تقرير JSON
gitleaks detect --source . --report-path reports/gitleaks.json
```

---

### 3. Static Analysis (التحليل الثابت)

#### Bandit (Python)

```bash
# تثبيت Bandit
pip install bandit

# فحص الكود
bandit -r backend/ -f json -o reports/bandit.json

# فحص مع مستوى عالي فقط
bandit -r backend/ -ll
```

#### Semgrep

```bash
# تثبيت Semgrep
pip install semgrep

# فحص الكود
semgrep --config=auto backend/

# فحص مع قواعد OWASP
semgrep --config=p/owasp-top-ten backend/
```

---

### 4. Container Scanning (فحص الحاويات)

#### Trivy

```bash
# تثبيت Trivy
brew install trivy  # macOS
# أو: https://github.com/aquasecurity/trivy

# فحص صورة Docker
trivy image mkh_manus:latest

# فحص مع تقرير JSON
trivy image --format json --output reports/trivy.json mkh_manus:latest

# فحص الثغرات الحرجة فقط
trivy image --severity CRITICAL,HIGH mkh_manus:latest
```

#### Docker Scout

```bash
# فحص الصورة
docker scout cves mkh_manus:latest

# فحص مع توصيات
docker scout recommendations mkh_manus:latest
```

---

## 📊 فحوصات الأداء

### 1. Load Testing (اختبار الحمل)

#### Locust

```bash
# تثبيت Locust
pip install locust

# تشغيل اختبار الحمل
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

#### Apache Bench

```bash
# اختبار endpoint محدد
ab -n 1000 -c 10 http://localhost:8000/api/v1/health

# اختبار مع POST
ab -n 100 -c 10 -p data.json -T application/json http://localhost:8000/api/v1/tasks
```

---

### 2. Memory Profiling (فحص الذاكرة)

```bash
# تثبيت memory_profiler
pip install memory_profiler

# تشغيل مع profiling
python -m memory_profiler backend/app/main.py
```

---

## 🔄 CI/CD Integration

### GitHub Actions

جميع الفحوصات مدمجة في `.github/workflows/ci.yml`:

```bash
# تشغيل CI محلياً (باستخدام act)
brew install act
act push
```

---

## 📋 قائمة الفحص الشاملة

قبل كل إصدار، تأكد من تشغيل:

### ✅ فحوصات الكود
- [ ] Flake8 (Python linting)
- [ ] ESLint (JavaScript/TypeScript linting)
- [ ] Black (Python formatting)
- [ ] Prettier (JavaScript/TypeScript formatting)
- [ ] MyPy (Python type checking)
- [ ] TypeScript compiler

### ✅ الاختبارات
- [ ] Unit tests (Backend)
- [ ] Unit tests (Frontend)
- [ ] Integration tests
- [ ] Smoke tests
- [ ] تغطية الكود > 80%

### ✅ الأمان
- [ ] Safety (Python dependencies)
- [ ] pnpm audit (Node.js dependencies)
- [ ] Detect-secrets (secret scanning)
- [ ] Gitleaks (secret scanning)
- [ ] Bandit (Python security)
- [ ] Semgrep (static analysis)
- [ ] Trivy (container scanning)

### ✅ البناء
- [ ] Docker build successful
- [ ] Frontend build successful
- [ ] No build warnings
- [ ] All services start correctly

### ✅ التوثيق
- [ ] README.md محدث
- [ ] SECURITY.md محدث
- [ ] API documentation محدثة
- [ ] CHANGELOG.md محدث

---

## 🚀 تشغيل جميع الفحوصات

يمكنك تشغيل جميع الفحوصات باستخدام سكريبت واحد:

```bash
# تشغيل validation.sh
./validation.sh

# أو تشغيل master_validation.sh للفحص الشامل
./master_validation.sh
```

---

## 📈 التقارير

جميع التقارير يتم حفظها في مجلد `reports/`:

```
reports/
├── flake8/
├── coverage/
├── safety.json
├── npm-audit.json
├── gitleaks.json
├── bandit.json
├── trivy.json
└── test-results.xml
```

---

## 🔧 أدوات إضافية مفيدة

### Pre-commit Hooks

```bash
# تثبيت pre-commit
pip install pre-commit

# إعداد hooks
pre-commit install

# تشغيل على جميع الملفات
pre-commit run --all-files
```

### SonarQube

```bash
# تشغيل SonarQube محلياً
docker run -d --name sonarqube -p 9000:9000 sonarqube:latest

# فحص المشروع
sonar-scanner \
  -Dsonar.projectKey=mkh_manus \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://localhost:9000
```

---

## 📚 مراجع

- [Pytest Documentation](https://docs.pytest.org/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Semgrep Documentation](https://semgrep.dev/docs/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

</div>
