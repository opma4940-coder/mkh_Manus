# ═══════════════════════════════════════════════════════════════════════════════
# Telegram Connector - موصل تيلجرام (مُنفّذ بالكامل)
# ═══════════════════════════════════════════════════════════════════════════════

import logging
import requests
from typing import List, Dict, Any, Optional

from .base import BaseConnector, ConnectorCapability, ConnectorAuthType

logger = logging.getLogger(__name__)

class TelegramConnector(BaseConnector):
    """
    موصل تيلجرام باستخدام Telegram Bot API.
    يوفر إرسال واستقبال الرسائل والملفات.
    """
    
    def __init__(self, connector_id: str, name: str, config: Dict[str, Any]):
        super().__init__(
            connector_id=connector_id,
            name=name,
            connector_type="telegram",
            capabilities=[
                ConnectorCapability.READ,
                ConnectorCapability.WRITE,
                ConnectorCapability.UPLOAD,
                ConnectorCapability.REALTIME
            ],
            auth_type=ConnectorAuthType.TOKEN,
            config=config
        )
        self.token = config.get("token")
        self.chat_id = config.get("chat_id")
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    async def connect(self) -> bool:
        """التحقق من صحة التوكن."""
        try:
            response = requests.get(f"{self.base_url}/getMe")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Telegram connection failed: {e}")
            return False

    async def disconnect(self) -> bool:
        return True

    async def send(self, payload: Dict[str, Any], attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        إرسال رسالة أو ملف إلى تيلجرام.
        payload: { "text": "message text", "chat_id": "optional_chat_id" }
        """
        chat_id = payload.get("chat_id", self.chat_id)
        text = payload.get("text", "")
        
        try:
            results = []
            
            # إرسال النص
            if text:
                resp = requests.post(f"{self.base_url}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML"
                })
                results.append(resp.json())
            
            # إرسال المرفقات
            if attachments:
                for file_path in attachments:
                    with open(file_path, "rb") as f:
                        resp = requests.post(f"{self.base_url}/sendDocument", data={
                            "chat_id": chat_id
                        }, files={
                            "document": f
                        })
                        results.append(resp.json())
            
            return {"success": True, "results": results}
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            return {"success": False, "error": str(e)}

    async def fetch(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        جلب آخر الرسائل (Updates).
        params: { "offset": 0, "limit": 10 }
        """
        offset = params.get("offset", 0)
        limit = params.get("limit", 10)
        
        try:
            resp = requests.get(f"{self.base_url}/getUpdates", params={
                "offset": offset,
                "limit": limit
            })
            updates = resp.json().get("result", [])
            
            results = []
            for update in updates:
                msg = update.get("message", {})
                results.append({
                    "update_id": update.get("update_id"),
                    "from": msg.get("from", {}).get("username"),
                    "text": msg.get("text"),
                    "date": msg.get("date"),
                    "chat_id": msg.get("chat", {}).get("id")
                })
            return results
        except Exception as e:
            logger.error(f"Telegram fetch failed: {e}")
            return []

    async def upload(self, local_path: str, remote_path: str) -> bool:
        """رفع ملف كـ Document (remote_path هو chat_id في هذا السياق)."""
        chat_id = remote_path or self.chat_id
        res = await self.send({"chat_id": chat_id}, attachments=[local_path])
        return res.get("success", False)
