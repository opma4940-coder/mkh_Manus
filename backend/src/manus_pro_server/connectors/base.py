# ═══════════════════════════════════════════════════════════════════════════════
# Base Connector Interface - الواجهة الأساسية للموصلات (مُحسّنة)
# ═══════════════════════════════════════════════════════════════════════════════

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConnectorCapability(Enum):
    """قدرات الموصل"""
    READ = "read"
    WRITE = "write"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    SEARCH = "search"
    SYNC = "sync"
    REALTIME = "realtime"

class ConnectorAuthType(Enum):
    """أنواع المصادقة"""
    NONE = "none"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    TOKEN = "token"

class BaseConnector(ABC):
    """الواجهة الأساسية لجميع الموصلات"""
    
    def __init__(
        self, 
        connector_id: str, 
        name: str, 
        connector_type: str,
        capabilities: List[ConnectorCapability],
        auth_type: ConnectorAuthType,
        config: Dict[str, Any]
    ):
        self.connector_id = connector_id
        self.name = name
        self.connector_type = connector_type
        self.capabilities = capabilities
        self.auth_type = auth_type
        self.config = config
        self.is_connected = False

    @abstractmethod
    async def connect(self) -> bool:
        """إنشاء اتصال مع الخدمة"""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """إغلاق الاتصال"""
        pass

    @abstractmethod
    async def send(self, payload: Dict[str, Any], attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """إرسال بيانات أو تنفيذ إجراء"""
        pass

    @abstractmethod
    async def fetch(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """جلب بيانات أو سرد محتويات"""
        pass

    async def upload(self, local_path: str, remote_path: str) -> bool:
        """رفع ملف (اختياري)"""
        if ConnectorCapability.UPLOAD not in self.capabilities:
            raise NotImplementedError("هذا الموصل لا يدعم الرفع")
        return False

    async def download(self, remote_path: str, local_path: str) -> bool:
        """تنزيل ملف (اختياري)"""
        if ConnectorCapability.DOWNLOAD not in self.capabilities:
            raise NotImplementedError("هذا الموصل لا يدعم التنزيل")
        return False

class OAuthConnector(BaseConnector):
    """موصل يدعم OAuth 2.0"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, auth_type=ConnectorAuthType.OAUTH2, **kwargs)
        self.access_token = self.config.get("access_token")
        self.refresh_token = self.config.get("refresh_token")
        self.expires_at = self.config.get("expires_at")

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """توليد رابط التفويض"""
        raise NotImplementedError()

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """تبادل الرمز بـ Access Token"""
        raise NotImplementedError()

    async def refresh_access_token(self) -> Dict[str, Any]:
        
        raise NotImplementedError()
