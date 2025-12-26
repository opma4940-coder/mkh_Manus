# ═══════════════════════════════════════════════════════════════════════════════
# Google Drive Connector - موصل جوجل درايف (مُنفّذ بالكامل)
# ═══════════════════════════════════════════════════════════════════════════════

import logging
import requests
from typing import List, Dict, Any, Optional

from .base import OAuthConnector, ConnectorCapability

logger = logging.getLogger(__name__)

class GoogleDriveConnector(OAuthConnector):
    """
    موصل جوجل درايف باستخدام Google Drive API v3.
    يوفر إدارة الملفات، الرفع، التنزيل، والبحث.
    """
    
    def __init__(self, connector_id: str, name: str, config: Dict[str, Any]):
        super().__init__(
            connector_id=connector_id,
            name=name,
            connector_type="google_drive",
            capabilities=[
                ConnectorCapability.READ,
                ConnectorCapability.WRITE,
                ConnectorCapability.UPLOAD,
                ConnectorCapability.DOWNLOAD,
                ConnectorCapability.SEARCH,
                ConnectorCapability.SYNC
            ],
            config=config
        )
        self.base_url = "https://www.googleapis.com/drive/v3"
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    async def connect(self) -> bool:
        """التحقق من صحة التوكن."""
        try:
            resp = requests.get(f"{self.base_url}/about", headers=self.headers, params={"fields": "user"})
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"GoogleDrive connection failed: {e}")
            return False

    async def disconnect(self) -> bool:
        return True

    async def send(self, payload: Dict[str, Any], attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        إنشاء مجلد أو ملف نصي بسيط.
        payload: { "name": "folder_name", "mimeType": "application/vnd.google-apps.folder" }
        """
        try:
            resp = requests.post(f"{self.base_url}/files", headers=self.headers, json=payload)
            return resp.json()
        except Exception as e:
            logger.error(f"GoogleDrive send failed: {e}")
            return {"success": False, "error": str(e)}

    async def fetch(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        سرد الملفات أو البحث.
        params: { "q": "name contains 'test'", "pageSize": 10 }
        """
        try:
            resp = requests.get(f"{self.base_url}/files", headers=self.headers, params=params)
            return resp.json().get("files", [])
        except Exception as e:
            logger.error(f"GoogleDrive fetch failed: {e}")
            return []

    async def upload(self, local_path: str, remote_path: str) -> bool:
        """رفع ملف إلى جوجل درايف."""
        try:
            metadata = {"name": remote_path}
            files = {
                "data": ("metadata", str(metadata), "application/json; charset=UTF-8"),
                "file": open(local_path, "rb")
            }
            resp = requests.post(
                "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
                headers=self.headers,
                files=files
            )
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"GoogleDrive upload failed: {e}")
            return False

    async def download(self, remote_path: str, local_path: str) -> bool:
        """تنزيل ملف من جوجل درايف (remote_path هو file_id)."""
        try:
            resp = requests.get(f"{self.base_url}/files/{remote_path}", headers=self.headers, params={"alt": "media"})
            if resp.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(resp.content)
                return True
            return False
        except Exception as e:
            logger.error(f"GoogleDrive download failed: {e}")
            return False

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        client_id = self.config.get("client_id")
        redirect_uri = self.config.get("redirect_uri")
        scope = "https://www.googleapis.com/auth/drive"
        return f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}&state={state}&access_type=offline&prompt=consent"

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        data = {
            "client_id": self.config.get("client_id"),
            "client_secret": self.config.get("client_secret"),
            "code": code,
            "redirect_uri": self.config.get("redirect_uri"),
            "grant_type": "authorization_code"
        }
        resp = requests.post("https://oauth2.googleapis.com/token", data=data)
        return resp.json()
