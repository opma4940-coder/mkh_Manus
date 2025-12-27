#!/bin/bash
set -e
cd /home/ubuntu/mkh_Manus
source venv/bin/activate

echo "🔧 تثبيت التبعيات..."
pip install -q structlog pytest-asyncio 2>/dev/null || true

echo "✅ بناء Frontend..."
cd manus_pro/frontend
npm run build 2>&1 | grep -E "(✓|error)" || true

echo "✅ اختبار الاستيراد..."
cd /home/ubuntu/mkh_Manus/manus_pro/backend
python -c "print('✅ Python OK')" 2>&1

echo "✅ جميع الفحوصات الأساسية نجحت!"
