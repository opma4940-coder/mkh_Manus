import pytest
from manus_pro_server import crypto
from manus_pro_server.auth import create_access_token, verify_password, get_password_hash

def test_encryption_decryption():
    # اختبار التشفير وفك التشفير
    original_text = "secret_token_123"
    encrypted = crypto.encrypt(original_text.encode())
    decrypted = crypto.decrypt(encrypted).decode()
    assert decrypted == original_text
    assert encrypted != original_text.encode()

def test_password_hashing():
    # اختبار تجزئة كلمة المرور
    password = "strong_password"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_jwt_token_creation():
    # اختبار إنشاء توكن JWT
    data = {"sub": "user_123", "role": "admin"}
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 10
