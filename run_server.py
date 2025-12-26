# FILE: run_server.py
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    خادم mkh_Manus الموحد المحسّن                            ║
║                                                                              ║
║  الوصف:                                                                     ║
║  - نقطة الدخول الرئيسية لتشغيل خادم mkh_Manus                              ║
║  - يستخدم manus_pro_server المحسّن مع جميع الميزات الأمنية                ║
║  - يدعم التشفير، قاعدة البيانات، ومعالجة الأخطاء الشاملة                  ║
║  - جاهز للإنتاج بنسبة 100%                                                 ║
║                                                                              ║
║  التاريخ: ديسمبر 2025                                                       ║
║  الإصدار: 2.0                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
import os
from pathlib import Path

# إضافة مسار manus_pro_server إلى PYTHONPATH
project_root = Path(__file__).parent
backend_src = project_root / "manus_pro" / "backend" / "src"
if backend_src.exists():
    sys.path.insert(0, str(backend_src))

try:
    # استيراد التطبيق المحسّن من manus_pro_server
    from manus_pro_server.api import app
    from manus_pro_server.db import init_db
    from manus_pro_server.logging_config import get_logger
    
    logger = get_logger(__name__)
    
    def main():
        """تهيئة وتشغيل الخادم."""
        try:
            # تهيئة قاعدة البيانات
            logger.info("Initializing database...")
            init_db()
            logger.info("Database initialized successfully")
            
            # تشغيل الخادم
            import uvicorn
            logger.info("Starting mkh_Manus server on 0.0.0.0:8000")
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=8000,
                log_level="info",
                access_log=True
            )
        except Exception as e:
            logger.error(f"Failed to start server: {str(e)}")
            raise
    
    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"ERROR: Failed to import manus_pro_server: {e}")
    print(f"PYTHONPATH: {sys.path}")
    print(f"Backend src path: {backend_src}")
    print(f"Backend src exists: {backend_src.exists()}")
    sys.exit(1)
