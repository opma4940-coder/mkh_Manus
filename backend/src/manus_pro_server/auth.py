# ═══════════════════════════════════════════════════════════════════════════════
# نظام المصادقة والتفويض لنظام mkh_Manus
# يوفر JWT + RBAC + Rate Limiting
# التاريخ: ديسمبر 2025
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address

# ═══ Configuration ═══
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 30

# ═══ Password Hashing ═══
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """التحقق من كلمة المرور"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """تشفير كلمة المرور"""
    return pwd_context.hash(password)

# ═══ JWT Token Operations ═══
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    إنشاء رمز وصول JWT
    
    Args:
        data: البيانات المراد تشفيرها
        expires_delta: مدة الصلاحية
    
    Returns:
        رمز JWT
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    إنشاء رمز تجديد JWT
    
    Args:
        data: البيانات المراد تشفيرها
    
    Returns:
        رمز JWT
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """
    فك تشفير رمز JWT
    
    Args:
        token: رمز JWT
    
    Returns:
        البيانات المشفرة
    
    Raises:
        HTTPException: إذا كان الرمز غير صالح
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ═══ Authentication Dependencies ═══
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    الحصول على المستخدم الحالي من رمز JWT
    
    Args:
        credentials: بيانات الاعتماد
    
    Returns:
        معلومات المستخدم
    
    Raises:
        HTTPException: إذا كان الرمز غير صالح
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    # الحصول على المستخدم من قاعدة البيانات
    from . import db
    user = db.get_user_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    return user

async def get_current_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    الحصول على المستخدم المسؤول الحالي
    
    Args:
        current_user: المستخدم الحالي
    
    Returns:
        معلومات المستخدم المسؤول
    
    Raises:
        HTTPException: إذا لم يكن المستخدم مسؤولاً
    """
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return current_user

# ═══ RBAC (Role-Based Access Control) ═══
class Permission:
    """الصلاحيات المتاحة"""
    
    # Tasks
    TASK_CREATE = "task:create"
    TASK_READ = "task:read"
    TASK_UPDATE = "task:update"
    TASK_DELETE = "task:delete"
    TASK_CANCEL = "task:cancel"
    
    # Settings
    SETTING_READ = "setting:read"
    SETTING_WRITE = "setting:write"
    
    # Connectors
    CONNECTOR_CREATE = "connector:create"
    CONNECTOR_READ = "connector:read"
    CONNECTOR_UPDATE = "connector:update"
    CONNECTOR_DELETE = "connector:delete"
    
    # Admin
    ADMIN_ALL = "admin:all"
    USER_MANAGE = "user:manage"
    AUDIT_READ = "audit:read"

class Role:
    """الأدوار المتاحة"""
    
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

# تعيين الصلاحيات للأدوار
ROLE_PERMISSIONS = {
    Role.ADMIN: [Permission.ADMIN_ALL],  # المسؤول لديه جميع الصلاحيات
    Role.USER: [
        Permission.TASK_CREATE,
        Permission.TASK_READ,
        Permission.TASK_UPDATE,
        Permission.TASK_CANCEL,
        Permission.SETTING_READ,
        Permission.SETTING_WRITE,
        Permission.CONNECTOR_CREATE,
        Permission.CONNECTOR_READ,
        Permission.CONNECTOR_UPDATE,
        Permission.CONNECTOR_DELETE,
    ],
    Role.VIEWER: [
        Permission.TASK_READ,
        Permission.SETTING_READ,
        Permission.CONNECTOR_READ,
    ],
}

def has_permission(user: Dict[str, Any], permission: str) -> bool:
    """
    التحقق من صلاحية المستخدم
    
    Args:
        user: معلومات المستخدم
        permission: الصلاحية المطلوبة
    
    Returns:
        True إذا كان المستخدم لديه الصلاحية
    """
    # المسؤول لديه جميع الصلاحيات
    if user.get("is_admin"):
        return True
    
    # الحصول على دور المستخدم
    role = user.get("role", Role.USER)
    
    # الحصول على صلاحيات الدور
    permissions = ROLE_PERMISSIONS.get(role, [])
    
    # التحقق من الصلاحية
    return permission in permissions or Permission.ADMIN_ALL in permissions

def require_permission(permission: str):
    """
    Decorator للتحقق من الصلاحية
    
    Args:
        permission: الصلاحية المطلوبة
    
    Returns:
        Dependency function
    """
    async def permission_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}",
            )
        return current_user
    
    return permission_checker

# ═══ Rate Limiting ═══
limiter = Limiter(key_func=get_remote_address)

def rate_limit(limit: str):
    """
    Decorator لتحديد معدل الطلبات
    
    Args:
        limit: الحد الأقصى (مثل: "60/minute", "1000/hour")
    
    Returns:
        Decorator function
    """
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator

# ═══ Audit Logging ═══
async def log_audit(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
) -> None:
    """
    تسجيل حدث تدقيق
    
    Args:
        user_id: معرف المستخدم
        action: الإجراء
        resource_type: نوع المورد
        resource_id: معرف المورد
        details: تفاصيل إضافية
        request: طلب HTTP
    """
    from . import db
    
    ip_address = None
    user_agent = None
    
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
    
    db.create_audit_log(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )

# ═══ API Key Authentication (for external services) ═══
async def verify_api_key(api_key: str) -> bool:
    """
    التحقق من مفتاح API
    
    Args:
        api_key: مفتاح API
    
    Returns:
        True إذا كان المفتاح صالحاً
    """
    from . import db
    
    # التحقق من قاعدة البيانات
    valid = db.verify_api_key(api_key)
    
    return valid

async def get_api_key_user(api_key: str = Depends(HTTPBearer())) -> Dict[str, Any]:
    """
    الحصول على المستخدم من مفتاح API
    
    Args:
        api_key: مفتاح API
    
    Returns:
        معلومات المستخدم
    
    Raises:
        HTTPException: إذا كان المفتاح غير صالح
    """
    if not await verify_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    from . import db
    user = db.get_user_by_api_key(api_key)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    return user
