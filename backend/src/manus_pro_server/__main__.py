# نقطة تشغيل بسيطة لـ Backend API.
# - تم إضافة فتح المتصفح تلقائياً عند التشغيل (توصية المستخدم).

from __future__ import annotations

import os
import webbrowser
import uvicorn
from .logging_config import get_logger # استيراد التسجيل المنظم

logger = get_logger(__name__)

def main():
    host = os.getenv("MANUS_PRO_HOST", "0.0.0.0")
    port = int(os.getenv("MANUS_PRO_PORT", "8000"))
    
    # فتح المتصفح تلقائياً (توصية المستخدم)
    # نستخدم 127.0.0.1 لضمان الفتح المحلي
    frontend_url = f"http://127.0.0.1:{port}"
    
    # تأخير بسيط لضمان أن الخادم بدأ الاستماع
    def open_browser_after_delay():
        import time
        time.sleep(1)
        backend_url = f"http://{host}:{port}/"
        logger.info("Attempting to open browser", url=backend_url)
        # Avoid opening browser in Codespaces or CI environments
        if not os.environ.get('CODESPACES') and not os.environ.get('CI'):
            try:
                webbrowser.open(backend_url)
            except Exception:
                logger.info('Could not open browser automatically')

    # تشغيل الدالة في خيط منفصل لتجنب حظر uvicorn
    import threading
    threading.Thread(target=open_browser_after_delay, daemon=True).start()
    
    logger.info("Starting Uvicorn server", host=host, port=port)
    uvicorn.run("manus_pro_server.api:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    main()
