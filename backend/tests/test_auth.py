import pytest
from datetime import timedelta
from app.auth import create_access_token, verify_token
from app.config import settings

def test_create_token():
    """测试创建 token"""
    data = {"sub": "admin"}
    token = create_access_token(data)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0

def test_verify_valid_token():
    """测试验证有效的 token"""
    data = {"sub": "admin"}
    token = create_access_token(data)

    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "admin"

def test_verify_invalid_token():
    """测试验证无效的 token"""
    invalid_token = "invalid.token.string"

    payload = verify_token(invalid_token)
    assert payload is None
