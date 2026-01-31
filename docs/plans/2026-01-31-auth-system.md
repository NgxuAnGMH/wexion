# 认证系统实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 为 Wexion CMS 构建基础的用户认证系统，包括登录功能、JWT 身份验证和受保护路由

**架构:** 前后端分离架构，使用 FastAPI 提供 REST API，Vike + Vue 3 构建前端界面，JWT token 存储在 localStorage 进行身份验证，SQLite 存储用户数据

**技术栈:**
- 后端: FastAPI + Python 3.13 + SQLAlchemy + SQLite + JWT + bcrypt
- 前端: Vike + Vue 3 + TypeScript + Axios
- 配置: PyYAML

---

## Task 1: 后端配置管理模块

**Files:**
- Create: `backend/app/config.py`
- Create: `backend/config.yaml`

**Step 1: 创建配置文件**

创建 `backend/config.yaml`:

```yaml
admin:
  username: "admin"
  password: "admin123"

jwt:
  secret_key: "your-secret-key-change-in-production"
  algorithm: "HS256"
  expire_minutes: 1440  # 24 小时

database:
  url: "sqlite:///./wexion.db"
```

**Step 2: 编写配置加载模块**

创建 `backend/app/config.py`:

```python
from pydantic_settings import BaseSettings
from pydantic import BaseModel
from typing import Literal
import yaml
from pathlib import Path

class AdminConfig(BaseModel):
    username: str
    password: str

class JWTConfig(BaseModel):
    secret_key: str
    algorithm: Literal["HS256"]
    expire_minutes: int

class DatabaseConfig(BaseModel):
    url: str

class Settings(BaseModel):
    admin: AdminConfig
    jwt: JWTConfig
    database: DatabaseConfig

def load_config() -> Settings:
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    return Settings(**config_data)

settings = load_config()
```

**Step 3: 测试配置加载**

运行测试:
```bash
cd backend
uv run python -c "from app.config import settings; print(settings.admin.username)"
```

预期输出: `admin`

**Step 4: 提交**

```bash
cd /home/cmx714/myHomeDir/github/wexion/.worktrees/auth-system
git add backend/config.yaml backend/app/config.py
git commit -m "feat: add configuration management module

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: 数据库模型和连接

**Files:**
- Create: `backend/app/database.py`
- Create: `backend/app/models.py`

**Step 1: 编写数据库连接模块**

创建 `backend/app/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.database.url,
    connect_args={"check_same_thread": False}  # SQLite 需要
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 2: 编写用户模型**

创建 `backend/app/models.py`:

```python
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    avatar = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Step 3: 初始化数据库**

创建 `backend/app/init_db.py`:

```python
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
```

**Step 4: 测试数据库初始化**

运行:
```bash
cd backend
uv run python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine); print('Database created')"
uv run python app/init_db.py
```

预期输出:
```
Database created
✅ 创建默认管理员账户: admin
```

**Step 5: 提交**

```bash
git add backend/app/database.py backend/app/models.py backend/app/init_db.py
git commit -m "feat: add database models and initialization

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: 密码加密工具

**Files:**
- Create: `backend/app/utils.py`
- Create: `backend/tests/test_utils.py`

**Step 1: 编写测试（TDD）**

创建 `backend/tests/test_utils.py`:

```python
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
```

**Step 2: 运行测试验证失败**

运行:
```bash
cd backend
uv run pytest tests/test_utils.py -v
```

预期: `FAILED` - `ModuleNotFoundError: app.utils`

**Step 3: 实现密码加密工具**

创建 `backend/app/utils.py`:

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)
```

**Step 4: 运行测试验证通过**

运行:
```bash
cd backend
uv run pytest tests/test_utils.py -v
```

预期: 3 个测试全部 `PASSED`

**Step 5: 提交**

```bash
git add backend/app/utils.py backend/tests/test_utils.py
git commit -m "feat: add password hashing utilities with tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: JWT 工具函数

**Files:**
- Create: `backend/app/auth.py`
- Create: `backend/tests/test_auth.py`

**Step 1: 编写测试**

创建 `backend/tests/test_auth.py`:

```python
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
```

**Step 2: 运行测试验证失败**

运行:
```bash
cd backend
uv run pytest tests/test_auth.py -v
```

预期: `FAILED` - `ModuleNotFoundError: app.auth`

**Step 3: 实现 JWT 工具**

创建 `backend/app/auth.py`:

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.config import settings

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt.expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)

    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """验证 JWT token"""
    try:
        payload = jwt.decode(token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm])
        return payload
    except JWTError:
        return None
```

**Step 4: 运行测试验证通过**

运行:
```bash
cd backend
uv run pytest tests/test_auth.py -v
```

预期: 3 个测试全部 `PASSED`

**Step 5: 提交**

```bash
git add backend/app/auth.py backend/tests/test_auth.py
git commit -m "feat: add JWT token utilities with tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Pydantic Schemas

**Files:**
- Create: `backend/app/schemas.py`

**Step 1: 创建数据验证模型**

创建 `backend/app/schemas.py`:

```python
from pydantic import BaseModel

class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str

class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    avatar: str | None = None

    class Config:
        from_attributes = True
```

**Step 2: 验证语法**

运行:
```bash
cd backend
uv run python -c "from app.schemas import LoginRequest, TokenResponse, UserResponse; print('Schemas imported successfully')"
```

预期: `Schemas imported successfully`

**Step 3: 提交**

```bash
git add backend/app/schemas.py
git commit -m "feat: add Pydantic schemas for request/response validation

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: 认证依赖注入

**Files:**
- Create: `backend/app/dependencies.py`
- Create: `backend/tests/test_dependencies.py`

**Step 1: 编写测试**

创建 `backend/tests/test_dependencies.py`:

```python
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

    # 模拟依赖注入
    from fastapi import Request
    request = Request({
        "type": "http",
        "headers": [(b"authorization", f"Bearer {token}".encode())],
    })

    # 注意: 这需要调整以适应实际的测试方式
    # 实际测试会在路由测试中进行

def test_get_current_user_with_invalid_token():
    """测试使用无效 token"""
    from fastapi import HTTPException

    # 这会在路由测试中验证
    pass
```

**Step 2: 创建依赖注入模块**

创建 `backend/app/dependencies.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import verify_token

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前认证用户"""
    token = credentials.credentials

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证失败，请重新登录"
        )

    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证失败，请重新登录"
        )

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )

    return user
```

**Step 3: 提交**

```bash
git add backend/app/dependencies.py backend/tests/test_dependencies.py
git commit -m "feat: add authentication dependency injection

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: 认证路由

**Files:**
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/routers/auth.py`
- Create: `backend/tests/test_auth_router.py`

**Step 1: 编写路由测试**

创建 `backend/tests/test_auth_router.py`:

```python
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

    response = client.get("/api/users/me", headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["id"] == user.id

def test_get_me_no_token():
    """测试未提供 token 访问受保护路由"""
    response = client.get("/api/users/me")

    assert response.status_code == 403  # HTTPBearer 返回 403

def test_get_me_invalid_token():
    """测试无效 token 访问受保护路由"""
    response = client.get("/api/users/me", headers={
        "Authorization": "Bearer invalid.token.here"
    })

    assert response.status_code == 401
```

**Step 2: 运行测试验证失败**

运行:
```bash
cd backend
uv run pytest tests/test_auth_router.py -v
```

预期: `FAILED` - 路由不存在

**Step 3: 实现认证路由**

创建 `backend/app/routers/__init__.py`:

```python
# Empty init file for routers package
```

创建 `backend/app/routers/auth.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, TokenResponse, UserResponse
from app.utils import verify_password
from app.auth import create_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户
    user = db.query(User).filter(User.username == credentials.username).first()

    # 验证用户和密码
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 生成 token
    access_token = create_access_token(data={"sub": user.username})

    return TokenResponse(access_token=access_token)

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user
```

**Step 4: 注册路由到主应用**

修改 `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth

app = FastAPI(title="Wexion CMS API")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5678"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Wexion CMS API"}
```

**Step 5: 运行测试验证通过**

运行:
```bash
cd backend
uv run pytest tests/test_auth_router.py -v
```

预期: 6 个测试全部 `PASSED`

**Step 6: 提交**

```bash
git add backend/app/routers/ backend/app/main.py backend/tests/test_auth_router.py
git commit -m "feat: add authentication routes with tests

- POST /api/auth/login - 用户登录
- GET /api/users/me - 获取当前用户信息
- Add CORS middleware for frontend

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: 用户路由（修正）

**Step 1: 修正路由位置**

修改 `backend/app/routers/auth.py`，将 `/api/auth/me` 移动到 `/api/users/me`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, TokenResponse, UserResponse
from app.utils import verify_password
from app.auth import create_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    access_token = create_access_token(data={"sub": user.username})
    return TokenResponse(access_token=access_token)
```

创建 `backend/app/routers/users.py`:

```python
from fastapi import APIRouter, Depends
from app.models import User
from app.schemas import UserResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/users", tags=["用户"])

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user
```

**Step 2: 更新主应用注册**

修改 `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users

app = FastAPI(title="Wexion CMS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5678"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "Wexion CMS API"}
```

**Step 3: 重新运行测试**

运行:
```bash
cd backend
uv run pytest tests/test_auth_router.py -v
```

预期: 所有测试 `PASSED`

**Step 4: 提交**

```bash
git add backend/app/routers/users.py backend/app/main.py
git commit -m "fix: separate user routes from auth routes

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: 前端 API 调用封装

**Files:**
- Create: `frontend/components/api.ts`

**Step 1: 创建 API 封装**

创建 `frontend/components/api.ts`:

```typescript
// API 基础配置
const API_BASE_URL = 'http://localhost:8000';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  username: string;
  avatar?: string;
}

// 获取存储的 token
export function getStoredToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token');
  }
  return null;
}

// 存储 token
export function setStoredToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('token', token);
  }
}

// 清除 token
export function clearStoredToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('token');
  }
}

// 登录 API
export async function login(credentials: LoginRequest): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '登录失败');
  }

  const data = await response.json() as TokenResponse;
  setStoredToken(data.access_token);
  return data;
}

// 获取当前用户信息 API
export async function getCurrentUser(): Promise<User> {
  const token = getStoredToken();

  if (!token) {
    throw new Error('未登录');
  }

  const response = await fetch(`${API_BASE_URL}/api/users/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      clearStoredToken();
    }
    const error = await response.json();
    throw new Error(error.detail || '获取用户信息失败');
  }

  return response.json() as Promise<User>;
}
```

**Step 2: 提交**

```bash
git add frontend/components/api.ts
git commit -m "feat: add API client wrapper with token management

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 10: 前端登录页面

**Files:**
- Create: `frontend/pages/login/+Page.vue`
- Create: `frontend/pages/login/+config.ts`

**Step 1: 创建登录页面配置**

创建 `frontend/pages/login/+config.ts`:

```typescript
// 登录页面配置
export default {
  title: '登录 - Wexion CMS',
};
```

**Step 2: 创建登录页面组件**

创建 `frontend/pages/login/+Page.vue`:

```vue
<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { login } from '../../components/api';

const router = useRouter();

const username = ref('');
const password = ref('');
const errorMessage = ref('');
const isLoading = ref(false);

async function handleLogin() {
  errorMessage.value = '';
  isLoading.value = true;

  try {
    await login({
      username: username.value,
      password: password.value,
    });

    // 登录成功，跳转到首页
    router.push('/home');
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '登录失败';
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-box">
      <h1>Wexion CMS</h1>
      <p class="subtitle">请登录</p>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="请输入用户名"
            required
            :disabled="isLoading"
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="请输入密码"
            required
            :disabled="isLoading"
          />
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <button type="submit" :disabled="isLoading">
          {{ isLoading ? '登录中...' : '登录' }}
        </button>
      </form>

      <div class="hint">
        <p>默认账户: admin / admin123</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 0.5rem;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #667eea;
}

input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.error-message {
  background-color: #fee;
  color: #c33;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  text-align: center;
}

button {
  width: 100%;
  padding: 0.75rem;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

button:hover:not(:disabled) {
  background-color: #5568d3;
}

button:disabled {
  background-color: #999;
  cursor: not-allowed;
}

.hint {
  margin-top: 1.5rem;
  text-align: center;
  color: #666;
  font-size: 0.875rem;
}
</style>
```

**Step 3: 提交**

```bash
git add frontend/pages/login/
git commit -m "feat: add login page with form validation

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 11: 前端首页

**Files:**
- Create: `frontend/pages/home/+Page.vue`
- Create: `frontend/pages/home/+config.ts`
- Create: `frontend/pages/home/+data.ts`

**Step 1: 创建首页配置**

创建 `frontend/pages/home/+config.ts`:

```typescript
export default {
  title: '首页 - Wexion CMS',
};
```

**Step 2: 创建首页数据获取**

创建 `frontend/pages/home/+data.ts`:

```typescript
import { getCurrentUser, User } from '../../components/api';

export default async function () {
  try {
    const user = await getCurrentUser();
    return {
      user,
    };
  } catch (error) {
    // 认证失败，返回 null
    return {
      user: null,
    };
  }
}
```

**Step 3: 创建首页组件**

创建 `frontend/pages/home/+Page.vue`:

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getCurrentUser, User, clearStoredToken } from '../../components/api';

const router = useRouter();

const user = ref<User | null>(null);
const isLoading = ref(true);
const errorMessage = ref('');

onMounted(async () => {
  try {
    const userData = await getCurrentUser();
    user.value = userData;
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '获取用户信息失败';
    // 自动跳转到登录页
    clearStoredToken();
    setTimeout(() => {
      router.push('/login');
    }, 2000);
  } finally {
    isLoading.value = false;
  }
});

function handleLogout() {
  clearStoredToken();
  router.push('/login');
}
</script>

<template>
  <div class="home-container">
    <header class="header">
      <h1>Wexion CMS</h1>
      <div class="user-info">
        <span v-if="user">欢迎, {{ user.username }}</span>
        <button @click="handleLogout" class="logout-btn">退出</button>
      </div>
    </header>

    <main class="main-content">
      <div v-if="isLoading" class="loading">
        加载中...
      </div>

      <div v-else-if="errorMessage" class="error">
        {{ errorMessage }}
        <p>即将跳转到登录页...</p>
      </div>

      <div v-else-if="user" class="welcome-card">
        <h2>欢迎使用 Wexion CMS</h2>
        <div class="user-details">
          <p><strong>用户 ID:</strong> {{ user.id }}</p>
          <p><strong>用户名:</strong> {{ user.username }}</p>
          <p v-if="user.avatar"><strong>头像:</strong> <img :src="user.avatar" alt="头像" /></p>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.home-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  background: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  margin: 0;
  color: #333;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logout-btn {
  padding: 0.5rem 1rem;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.logout-btn:hover {
  background-color: #5568d3;
}

.main-content {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.loading,
.error {
  text-align: center;
  padding: 2rem;
  font-size: 1.125rem;
}

.error {
  color: #c33;
}

.welcome-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.welcome-card h2 {
  margin-top: 0;
  color: #333;
}

.user-details {
  margin-top: 1.5rem;
}

.user-details p {
  margin-bottom: 0.75rem;
  color: #666;
}

.user-details img {
  max-width: 100px;
  border-radius: 4px;
}
</style>
```

**Step 4: 提交**

```bash
git add frontend/pages/home/
git commit -m "feat: add home page with user info display

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 12: 路由守卫

**Files:**
- Modify: `frontend/renderer/_default.tsx`

**Step 1: 查看当前渲染器**

检查:
```bash
cat /home/cmx714/myHomeDir/github/wexion/.worktrees/auth-system/frontend/renderer/_default.tsx
```

**Step 2: 添加路由守卫逻辑**

根据现有文件结构修改。如果文件不存在，创建它：

```typescript
// 为 Vike + Vue 配置
export default {
  // 可以添加全局配置
};
```

**注意**: Vike 使用文件系统路由，路由守卫应该在页面级别处理。我们已经在 `/home` 页面添加了认证检查。

**Step 3: 创建根路由重定向**

创建 `frontend/pages/index/+Page.vue`:

```vue
<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getStoredToken } from '../../components/api';

const router = useRouter();

onMounted(() => {
  const token = getStoredToken();
  if (token) {
    router.push('/home');
  } else {
    router.push('/login');
  }
});
</script>

<template>
  <div>正在跳转...</div>
</template>
```

**Step 4: 提交**

```bash
git add frontend/pages/index/ frontend/renderer/
git commit -m "feat: add root route redirect based on auth status

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 13: 前后端集成测试

**Files:**
- No new files

**Step 1: 启动后端服务器**

终端 1:
```bash
cd /home/cmx714/myHomeDir/github/wexion/.worktrees/auth-system/backend
uv run uvicorn app.main:app --reload --port 8000
```

预期输出:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Step 2: 启动前端服务器**

终端 2:
```bash
cd /home/cmx714/myHomeDir/github/wexion/.worktrees/auth-system/frontend
pnpm run dev --port 5678
```

预期输出:
```
  VITE v7.3.1  ready in 123 ms

  ➜  Local:   http://localhost:5678/
```

**Step 3: 测试登录流程**

在浏览器中访问 `http://localhost:5678`:

1. 应该自动跳转到 `/login`
2. 输入用户名: `admin`, 密码: `admin123`
3. 点击登录
4. 应该跳转到 `/home` 并显示用户信息

**Step 4: 测试受保护路由**

1. 刷新 `/home` 页面
2. 应该仍然显示用户信息（保持登录状态）

**Step 5: 测试未认证访问**

1. 打开浏览器开发者工具
2. 在 Console 中执行: `localStorage.removeItem('token')`
3. 刷新页面
4. 应该跳转到 `/login`

**Step 6: 手动测试 API**

```bash
# 测试登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 测试获取用户信息（替换 YOUR_TOKEN）
curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Step 7: 提交测试结果文档**

创建 `backend/TESTING.md`:

```markdown
# 测试说明

## 手动测试清单

- [ ] 登录成功
- [ ] 登录失败（错误密码）
- [ ] 访问受保护页面
- [ ] 刷新保持登录状态
- [ ] 清除 token 后重定向

## API 测试

```bash
# 启动服务
cd backend && uv run uvicorn app.main:app --reload

# 测试登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```
```

提交:
```bash
git add backend/TESTING.md
git commit -m "docs: add testing documentation

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 14: 最终验证和清理

**Step 1: 运行所有测试**

```bash
cd /home/cmx714/myHomeDir/github/wexion/.worktrees/auth-system/backend
uv run pytest -v
```

预期: 所有测试通过

**Step 2: 检查代码质量**

```bash
cd backend
uv run ruff check .
```

**Step 3: 验证端到端流程**

启动前后端，完整测试一遍:
1. 访问首页 → 跳转登录
2. 登录成功 → 跳转首页
3. 刷新页面 → 保持登录
4. 清除 token → 跳转登录

**Step 4: 创建 README**

创建 `backend/README_AUTH.md`:

```markdown
# 认证系统使用说明

## 快速开始

### 1. 初始化数据库

```bash
cd backend
uv run python app/init_db.py
```

### 2. 启动后端

```bash
uv run uvicorn app.main:app --reload
```

### 3. 启动前端

```bash
cd frontend
pnpm run dev --port 5678
```

### 4. 访问

打开浏览器: http://localhost:5678

默认账户: `admin` / `admin123`

## API 接口

### POST /api/auth/login
用户登录

**请求:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### GET /api/users/me
获取当前用户信息（需要认证）

**请求头:**
```
Authorization: Bearer <token>
```

**响应:**
```json
{
  "id": 1,
  "username": "admin",
  "avatar": null
}
```

## 配置

修改 `backend/config.yaml` 来更改:
- 管理员账户
- JWT 密钥和过期时间
- 数据库路径
```

提交:
```bash
git add backend/README_AUTH.md
git commit -m "docs: add authentication system usage guide

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## 验收标准

完成所有任务后，系统应该满足:

- ✅ 用户可以登录并获取 JWT token
- ✅ Token 存储在 localStorage
- ✅ 受保护路由自动检查认证状态
- ✅ 未认证用户自动重定向到登录页
- ✅ 所有后端测试通过
- ✅ 前后端集成测试通过
- ✅ 代码已提交到 feature/auth-system 分支

## 下一步

实施完成后，可以考虑:
- 添加登出功能
- 添加密码修改功能
- 添加 Refresh Token 机制
- 迁移到 PostgreSQL
- 添加用户管理界面
