# طبقة التشفير والأمان لنظام mkh_Manus:
# - يستخدم تشفير Fernet (AES-128 في وضع CBC مع HMAC-SHA256).
# - يدير توليد وتخزين مفتاح التشفير الرئيسي بشكل آمن.
# - يضمن أذونات ملفات صارمة (0o600) لحماية المفاتيح على القرص.
# - يوفر وظائف بسيطة وآمنة لتشفير وفك تشفير النصوص (مثل مفاتيح API).
# - مصمم ليكون تنفيذياً بنسبة 100% وجاهزاً للإنتاج الفعلي في ديسمبر 2025.

from __future__ import annotations
import os
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from .config import FERNET_KEY_PATH
from .logging_config import get_logger

logger = get_logger(__name__)

_FERNET: Optional[Fernet] = None

def _ensure_file_permissions(path: Path) -> None:
    """تأمين الملف بأذونات صارمة (للمالك فقط)."""
    try:
        os.chmod(path, 0o600)
    except Exception as e:
        logger.warning(f"Could not set strict permissions on {path}: {e}")

def load_or_create_fernet() -> Fernet:
    """تحميل مفتاح التشفير من القرص أو إنشاء مفتاح جديد إذا لم يوجد."""
    path = FERNET_KEY_PATH
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        key = Fernet.generate_key()
        path.write_bytes(key)
        _ensure_file_permissions(path)
        logger.info(f"New encryption key generated and secured at {path}")
    else:
        _ensure_file_permissions(path)
    return Fernet(path.read_bytes())

def get_key() -> Fernet:
    """تحميل أو إنشاء مفتاح Fernet وضمان تهيئة الكائن العام."""
    global _FERNET
    if _FERNET is None:
        _FERNET = load_or_create_fernet()
    return _FERNET

def encrypt_str(value: str) -> str:
    """تشفير سلسلة نصية وإرجاعها كسلسلة نصية مشفرة (Base64)."""
    if not value: return ""
    f = get_key()
    try:
        return f.encrypt(value.encode("utf-8")).decode("utf-8")
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise

def decrypt_str(token: str) -> str:
    """فك تشفير سلسلة نصية مشفرة (Base64) وإرجاع القيمة الأصلية."""
    if not token: return ""
    f = get_key()
    try:
        # دعم كل من str و bytes للمرونة
        token_bytes = token.encode("utf-8") if isinstance(token, str) else token
        return f.decrypt(token_bytes).decode("utf-8")
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        return "[DECRYPTION_FAILED]"

# أسماء مستعارة للتوافق مع الأجزاء الأخرى من النظام
encrypt = encrypt_str
decrypt = decrypt_str
