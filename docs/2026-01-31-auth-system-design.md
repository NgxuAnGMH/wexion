# 用户认证系统设计方案

**日期**: 2026-01-31
**项目**: Wexion CMS
**目标**: 构建基础的用户认证框架

---

## 1. 概述

本设计方案为 Wexion 内容管理系统（CMS）构建一个基础的用户认证框架，采用前后端分离架构，使用 JWT 进行身份验证。

### 1.1 核心功能

- 用户登录认证
- 受保护的路由访问
- 基于 SQLite 的用户数据存储
- 默认管理员账户配置

### 1.2 技术栈

**前端**:
- Vike + Vue 3 + TypeScript
- localStorage (Token 存储)
- Axios/Fetch (API 通信)

**后端**:
- FastAPI + Python 3.13
- SQLAlchemy (ORM)
- SQLite (数据库)
- JWT (身份验证)
- PyYAML (配置管理)

---

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │         │  Frontend    │         │   Backend   │
│             │◄───────►│  (Vike+Vue)  │◄───────►│  (FastAPI)  │
│  localhost  │  HTTP   │              │  API    │             │
│   :5678     │         │  :5678       │         │  :8000      │
└─────────────┘         └──────────────┘         └─────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────┐
                                                │   SQLite    │
                                                │  Database   │
                                                └─────────────┘
```

### 2.2 数据流

**登录流程**:
1. 用户在 `/login` 输入用户名和密码
2. 前端调用 `POST /api/auth/login`
3. 后端验证凭据，生成 JWT token
4. 前端将 token 存储到 localStorage
5. 跳转到 `/home`

**访问受保护页面**:
1. 用户访问 `/home`
2. 前端检查 localStorage 中的 token
3. 携带 token 调用 `GET /api/users/me`
4. 后端验证 token，返回用户信息
5. 前端显示页面内容

---

## 3. 数据库设计

### 3.1 用户表 (users)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PRIMARY KEY | 用户 ID |
| username | String(50) | UNIQUE, NOT NULL | 用户名（登录名） |
| hashed_password | String(200) | NOT NULL | bcrypt 加密密码 |
| avatar | String(500) | NULLABLE | 头像 URL |
| created_at | DateTime | DEFAULT utcnow | 创建时间 |

### 3.2 SQLAlchemy 模型

```python
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    avatar = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 4. API 设计

### 4.1 认证接口

#### POST /api/auth/login

**请求**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**成功响应** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**失败响应** (401):
```json
{
  "detail": "用户名或密码错误"
}
```

### 4.2 用户接口

#### GET /api/users/me

**请求头**:
```
Authorization: Bearer <token>
```

**成功响应** (200):
```json
{
  "id": 1,
  "username": "admin",
  "avatar": null
}
```

**失败响应** (401):
```json
{
  "detail": "认证失败，请重新登录"
}
```

---

## 5. 前端路由

### 5.1 路由结构

| 路由 | 访问控制 | 功能 |
|------|----------|------|
| `/login` | 公开 | 登录页面 |
| `/home` | 需要认证 | 欢迎页面 |
| `/*` | - | 重定向到 `/login` |

### 5.2 路由守卫逻辑

```
访问 /home
    ↓
检查 localStorage.token
    ↓
存在？        不存在
    ↓              ↓
调用 /api/users/me  跳转 /login
    ↓
成功？      失败 (401)
    ↓          ↓
显示页面    跳转 /login
```

---

## 6. 配置管理

### 6.1 config.yaml

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

### 6.2 密码加密

使用 `passlib` + `bcrypt`:
- 注册/创建用户时: `hash_password(password)`
- 登录验证时: `verify_password(plain_password, hashed_password)`

---

## 7. 错误处理

### 7.1 后端错误处理

| 场景 | 状态码 | 错误信息 |
|------|--------|----------|
| 用户名或密码错误 | 401 | 用户名或密码错误 |
| Token 过期 | 401 | 认证失败，请重新登录 |
| Token 签名无效 | 401 | 认证失败，请重新登录 |
| 数据库错误 | 500 | 服务器内部错误 |

### 7.2 前端错误处理

- 拦截 401 响应 → 清除 token，跳转 `/login`
- 拦截 500 响应 → 显示错误提示
- 拦截网络错误 → 显示连接失败提示

---

## 8. 安全措施

### 8.1 密码安全
- 使用 bcrypt 加密（自适应哈希）
- 不在日志中记录明文密码
- 密码最少 6 字符

### 8.2 Token 安全
- 设置过期时间（24 小时）
- 生产环境 secret_key 至少 32 位随机字符
- 验证 token 签名

### 8.3 输入验证
- 用户名: 3-50 字符，字母数字下划线
- 密码: 最少 6 字符

### 8.4 CORS 配置
- 只允许前端域名访问
- 正确配置 `Access-Control-Allow-Origin`

---

## 9. 项目结构

```
wexion/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── config.py            # 配置加载
│   │   ├── database.py          # 数据库连接
│   │   ├── models.py            # SQLAlchemy 模型
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # JWT 工具函数
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── auth.py          # 认证路由
│   │   └── utils.py             # 密码加密工具
│   ├── config.yaml              # 配置文件
│   └── wexion.db                # SQLite 数据库（自动生成）
├── frontend/
│   ├── pages/
│   │   ├── login/
│   │   │   └── +Page.vue        # 登录页面
│   │   └── home/
│   │       └── +Page.vue        # 首页
│   ├── components/
│   │   └── api.ts               # API 调用封装
│   └── renderer/
│       └── _default.tsx         # 全局状态管理
└── docs/
    └── plans/
        └── 2026-01-31-auth-system-design.md
```

---

## 10. 实施步骤

### 阶段 1: 后端基础
1. ✅ 配置文件加载（读取 `config.yaml`）
2. ✅ 数据库模型创建（User 表）
3. ✅ 密码加密工具（bcrypt）
4. ✅ 初始化默认管理员账户

### 阶段 2: 后端 API
5. ✅ JWT 工具函数（生成/验证 token）
6. ✅ 登录接口 `POST /api/auth/login`
7. ✅ 获取用户信息接口 `GET /api/users/me`
8. ✅ 认证中间件（依赖注入）

### 阶段 3: 前端页面
9. ✅ 创建登录页面 UI
10. ✅ 创建首页 UI
11. ✅ 路由守卫（未登录跳转）

### 阶段 4: 前后端联调
12. ✅ API 调用封装（axios/fetch）
13. ✅ localStorage 管理
14. ✅ 错误处理和提示
15. ✅ 端到端测试

---

## 11. 开发环境

### 启动服务

**后端** (默认端口 8000):
```bash
cd backend
uvicorn app.main:app --reload
```

**前端** (端口 5678):
```bash
cd frontend
pnpm run dev --port 5678
```

**访问**: http://localhost:5678/login

---

## 12. 测试清单

### 单元测试
- [ ] 密码加密/验证函数
- [ ] JWT 生成/验证函数
- [ ] 配置文件加载
- [ ] 数据库模型 CRUD

### API 测试
- [ ] 登录成功场景
- [ ] 登录失败场景（错误密码）
- [ ] Token 验证成功/失败
- [ ] 未认证访问受保护接口

### 集成测试
- [ ] 访问 `/login` → 检查页面渲染
- [ ] 输入错误密码 → 检查错误提示
- [ ] 输入正确凭据 → 检查登录成功
- [ ] 跳转到 `/home` → 检查显示用户信息
- [ ] 刷新页面 → 检查保持登录状态
- [ ] 清除 localStorage → 检查重定向到登录页

---

## 13. 后续扩展

### 功能扩展
- [ ] 登出功能
- [ ] 修改密码
- [ ] 修改头像
- [ ] 用户管理（CRUD）
- [ ] 角色权限系统

### 技术优化
- [ ] Refresh Token 机制
- [ ] Cookie 存储 (httpOnly)
- [ ] PostgreSQL 迁移
- [ ] Redis 缓存
- [ ] 日志系统
- [ ] 监控告警

---

**文档版本**: 1.0
**最后更新**: 2026-01-31
