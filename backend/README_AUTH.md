# 认证系统使用说明

## 快速开始

### 1. 初始化数据库

```bash
cd backend
PYTHONPATH=. uv run python -c "from app.init_db import init_db; init_db()"
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

## 测试

运行测试:
```bash
cd backend
uv run pytest -v
```

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── auth.py              # JWT 工具函数
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── dependencies.py      # 依赖注入
│   ├── init_db.py           # 数据库初始化
│   ├── main.py              # FastAPI 应用
│   ├── models.py            # SQLAlchemy 模型
│   ├── routers/             # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py          # 认证路由
│   │   └── users.py         # 用户路由
│   ├── schemas.py           # Pydantic schemas
│   └── utils.py             # 工具函数
├── tests/                   # 测试文件
├── config.yaml              # 配置文件
└── wexion.db                # SQLite 数据库
```

## 安全注意事项

⚠️ **重要**:
- 生产环境必须修改 `config.yaml` 中的默认密码和 JWT secret_key
- `config.yaml` 包含敏感信息，请勿提交到版本控制
- 建议使用环境变量管理敏感配置
