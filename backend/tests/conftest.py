import pytest
from app.database import SessionLocal

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
