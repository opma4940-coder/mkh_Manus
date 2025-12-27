# ═══════════════════════════════════════════════════════════════════════════════
# GitHub Connector - موصل جيت هوب (مُنفّذ بالكامل)
# ═══════════════════════════════════════════════════════════════════════════════

import logging
import requests
import base64
from typing import List, Dict, Any, Optional

from .base import OAuthConnector, ConnectorCapability

logger = logging.getLogger(__name__)

class GitHubConnector(OAuthConnector):
    """
    موصل جيت هوب باستخدام GitHub API.
    يوفر إدارة المستودعات والملفات والبحث.
    """
    
    def __init__(self, connector_id: str, name: str, config: Dict[str, Any]):
        super().__init__(
            connector_id=connector_id,
            name=name,
            connector_type="github",
            capabilities=[
                ConnectorCapability.READ,
                ConnectorCapability.WRITE,
                ConnectorCapability.UPLOAD,
                ConnectorCapability.SEARCH,
                ConnectorCapability.SYNC
            ],
            config=config
        )
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.access_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def connect(self) -> bool:
        """التحقق من صحة التوكن والوصول للملف الشخصي."""
        try:
            resp = requests.get(f"{self.base_url}/user", headers=self.headers)
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"GitHub connection failed: {e}")
            return False

    async def disconnect(self) -> bool:
        return True

    async def send(self, payload: Dict[str, Any], attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        إنشاء ملف أو تحديثه في مستودع.
        payload: { "repo": "user/repo", "path": "file.md", "message": "commit msg", "content": "text" }
        """
        repo = payload.get("repo")
        path = payload.get("path")
        message = payload.get("message", "Update from mkh_Manus")
        content = payload.get("content", "")
        branch = payload.get("branch", "main")
        
        try:
            # تحويل المحتوى إلى base64
            content_b64 = base64.b64encode(content.encode()).decode()
            
            # الحصول على sha للملف إذا كان موجوداً (للتحديث)
            sha = None
            resp = requests.get(f"{self.base_url}/repos/{repo}/contents/{path}", headers=self.headers, params={"ref": branch})
            if resp.status_code == 200:
                sha = resp.json().get("sha")
            
            # تنفيذ الـ commit
            data = {
                "message": message,
                "content": content_b64,
                "branch": branch
            }
            if sha:
                data["sha"] = sha
                
            resp = requests.put(f"{self.base_url}/repos/{repo}/contents/{path}", headers=self.headers, json=data)
            return resp.json()
        except Exception as e:
            logger.error(f"GitHub send failed: {e}")
            return {"success": False, "error": str(e)}

    async def fetch(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        جلب محتويات مستودع أو البحث.
        params: { "repo": "user/repo", "path": "dir", "q": "search query" }
        """
        repo = params.get("repo")
        path = params.get("path", "")
        query = params.get("q")
        
        try:
            if query:
                # بحث في الكود
                resp = requests.get(f"{self.base_url}/search/code", headers=self.headers, params={"q": f"{query} repo:{repo}" if repo else query})
                return resp.json().get("items", [])
            else:
                # سرد المحتويات
                resp = requests.get(f"{self.base_url}/repos/{repo}/contents/{path}", headers=self.headers)
                return resp.json() if isinstance(resp.json(), list) else [resp.json()]
        except Exception as e:
            logger.error(f"GitHub fetch failed: {e}")
            return []

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        client_id = self.config.get("client_id")
        redirect_uri = self.config.get("redirect_uri")
        scope = "repo user"
        return f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}"

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        data = {
            "client_id": self.config.get("client_id"),
            "client_secret": self.config.get("client_secret"),
            "code": code,
            "redirect_uri": self.config.get("redirect_uri")
        }
        resp = requests.post("https://github.com/login/oauth/access_token", headers={"Accept": "application/json"}, data=data)
        return resp.json()
