from app.database import engine, Base, SessionLocal
from app.models import User
from app.config import settings
from app.utils import hash_password

def init_db():
    """创建数据库表和默认管理员账户"""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 检查是否已存在管理员
        existing_admin = db.query(User).filter(User.username == settings.admin.username).first()
        if not existing_admin:
            admin = User(
                username=settings.admin.username,
                hashed_password=hash_password(settings.admin.password)
            )
            db.add(admin)
            db.commit()
            print(f"✅ 创建默认管理员账户: {settings.admin.username}")
        else:
            print(f"⚠️  管理员账户已存在: {settings.admin.username}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
