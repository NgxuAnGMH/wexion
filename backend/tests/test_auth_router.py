import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal

client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    """测试数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 清理: 删除所有测试数据
        from app.models import User
        db.query(User).delete()
        db.commit()

def test_login_success(db_session):
    """测试登录成功"""
    from app.models import User
    from app.utils import hash_password

    # 创建测试用户
    user = User(username="testuser", hashed_password=hash_password("test123"))
    db_session.add(user)
    db_session.commit()

    # 测试登录
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "test123"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(db_session):
    """测试登录失败（错误密码）"""
    from app.models import User
    from app.utils import hash_password

    # 创建测试用户
    user = User(username="testuser", hashed_password=hash_password("test123"))
    db_session.add(user)
    db_session.commit()

    # 测试登录
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    assert "用户名或密码错误" in response.json()["detail"]

def test_login_user_not_found(db_session):
    """测试登录失败（用户不存在）"""
    response = client.post("/api/auth/login", json={
        "username": "nonexistent",
        "password": "test123"
    })

    assert response.status_code == 401

def test_get_me_success(db_session):
    """测试获取当前用户信息成功"""
    from app.models import User
    from app.utils import hash_password
    from app.auth import create_access_token

    # 创建测试用户
    user = User(username="testuser", hashed_password=hash_password("test123"))
    db_session.add(user)
    db_session.commit()

    token = create_access_token({"sub": "testuser"})

    response = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["id"] == user.id

def test_get_me_no_token():
    """测试未提供 token 访问受保护路由"""
    response = client.get("/api/auth/me")

    assert response.status_code == 401  # HTTPBearer 返回 401

def test_get_me_invalid_token():
    """测试无效 token 访问受保护路由"""
    response = client.get("/api/auth/me", headers={
        "Authorization": "Bearer invalid.token.here"
    })

    assert response.status_code == 401
