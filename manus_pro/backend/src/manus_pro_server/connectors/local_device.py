# ═══════════════════════════════════════════════════════════════════════════════
# Local Device Connector - موصل الجهاز المحلي (مُنفّذ بالكامل)
# ═══════════════════════════════════════════════════════════════════════════════

import os
import shutil
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .base import BaseConnector, ConnectorCapability, ConnectorAuthType

logger = logging.getLogger(__name__)

class LocalDeviceConnector(BaseConnector):
    """
    موصل للجهاز المحلي (Windows, Linux, Mac, Android, iOS).
    يوفر الوصول إلى الملفات والمجلدات المحلية.
    """
    
    def __init__(self, connector_id: str, name: str, config: Dict[str, Any]):
        super().__init__(
            connector_id=connector_id,
            name=name,
            connector_type="local_device",
            capabilities=[
                ConnectorCapability.READ,
                ConnectorCapability.WRITE,
                ConnectorCapability.UPLOAD,
                ConnectorCapability.DOWNLOAD,
                ConnectorCapability.SEARCH
            ],
            auth_type=ConnectorAuthType.NONE,
            config=config
        )
        # تحديد مسار الجذر (default: /app/workspace)
        self.root_path = Path(config.get("root_path", "/app/workspace"))
        if not self.root_path.exists():
            self.root_path.mkdir(parents=True, exist_ok=True)

    async def connect(self) -> bool:
        """التحقق من إمكانية الوصول للمسار."""
        try:
            return self.root_path.exists() and os.access(self.root_path, os.R_OK | os.W_OK)
        except Exception as e:
            logger.error(f"LocalDevice connection failed: {e}")
            return False

    async def disconnect(self) -> bool:
        return True

    async def send(self, payload: Dict[str, Any], attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        كتابة بيانات إلى ملف محلي.
        payload: { "path": "relative/path/to/file.txt", "content": "text content", "mode": "w" }
        """
        target_path = self.root_path / payload.get("path", "output.txt")
        content = payload.get("content", "")
        mode = payload.get("mode", "w")
        
        try:
            # التأكد من وجود المجلدات
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_path, mode, encoding="utf-8") as f:
                f.write(content)
            
            # التعامل مع المرفقات (نسخها إلى المجلد)
            if attachments:
                attach_dir = target_path.parent / "attachments"
                attach_dir.mkdir(exist_ok=True)
                for attach in attachments:
                    if os.path.exists(attach):
                        shutil.copy(attach, attach_dir / os.path.basename(attach))

            return {
                "success": True,
                "path": str(target_path),
                "size": target_path.stat().st_size
            }
        except Exception as e:
            logger.error(f"LocalDevice send failed: {e}")
            return {"success": False, "error": str(e)}

    async def fetch(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        قراءة ملفات أو سرد مجلدات.
        params: { "path": "relative/path", "recursive": false }
        """
        search_path = self.root_path / params.get("path", "")
        recursive = params.get("recursive", False)
        
        try:
            if not search_path.exists():
                return []
            
            results = []
            if search_path.is_file():
                with open(search_path, "r", encoding="utf-8", errors="ignore") as f:
                    results.append({
                        "name": search_path.name,
                        "path": str(search_path),
                        "type": "file",
                        "content": f.read(10000), # أول 10 كيلو بايت
                        "size": search_path.stat().st_size
                    })
            else:
                pattern = "**/*" if recursive else "*"
                for p in search_path.glob(pattern):
                    results.append({
                        "name": p.name,
                        "path": str(p),
                        "type": "file" if p.is_file() else "directory",
                        "size": p.stat().st_size if p.is_file() else 0,
                        "modified": p.stat().st_mtime
                    })
            return results
        except Exception as e:
            logger.error(f"LocalDevice fetch failed: {e}")
            return []

    async def upload(self, local_path: str, remote_path: str) -> bool:
        """نسخ ملف من مكان آخر إلى مساحة العمل."""
        try:
            dest = self.root_path / remote_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(local_path, dest)
            return True
        except Exception as e:
            logger.error(f"LocalDevice upload failed: {e}")
            return False

    async def download(self, remote_path: str, local_path: str) -> bool:
        """نسخ ملف من مساحة العمل إلى مكان آخر."""
        try:
            src = self.root_path / remote_path
            if not src.exists():
                return False
            shutil.copy(src, local_path)
            return True
        except Exception as e:
            logger.error(f"LocalDevice download failed: {e}")
            return False
