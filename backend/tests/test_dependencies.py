import pytest
from fastapi import Depends
from app.dependencies import get_current_user
from app.auth import create_access_token

def test_get_current_user_with_valid_token(db_session):
    """测试使用有效 token 获取当前用户"""
    # 创建测试用户
    from app.models import User
    from app.utils import hash_password

    user = User(username="testuser", hashed_password=hash_password("test123"))
    db_session.add(user)
    db_session.commit()

    # 创建 token
    token = create_access_token({"sub": "testuser"})

    # 注意: 这需要调整以适应实际的测试方式
    # 实际测试会在路由测试中进行

def test_get_current_user_with_invalid_token():
    """测试使用无效 token"""
    from fastapi import HTTPException

    # 这会在路由测试中验证
    pass
