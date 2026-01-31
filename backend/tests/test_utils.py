import pytest
from app.utils import hash_password, verify_password

def test_hash_password():
    """测试密码哈希"""
    plain_password = "test123"
    hashed = hash_password(plain_password)

    # 哈希后的密码应该不同于原密码
    assert hashed != plain_password
    # bcrypt 哈希通常以 $2b$ 开头
    assert hashed.startswith("$2b$")

def test_verify_password_correct():
    """测试正确的密码验证"""
    plain_password = "test123"
    hashed = hash_password(plain_password)

    assert verify_password(plain_password, hashed) is True

def test_verify_password_wrong():
    """测试错误的密码验证"""
    plain_password = "test123"
    wrong_password = "wrong456"
    hashed = hash_password(plain_password)

    assert verify_password(wrong_password, hashed) is False
