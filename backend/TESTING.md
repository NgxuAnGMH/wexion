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

## 前后端集成测试步骤

### 1. 启动后端服务器

终端 1:
```bash
cd /home/cmx714/myHomeDir/github/wexion/.worktrees/auth-system/backend
uv run uvicorn app.main:app --reload --port 8000
```

预期输出:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 2. 启动前端服务器

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

### 3. 测试登录流程

在浏览器中访问 `http://localhost:5678`:

1. 应该自动跳转到 `/login`
2. 输入用户名: `admin`, 密码: `admin123`
3. 点击登录
4. 应该跳转到 `/home` 并显示用户信息

### 4. 测试受保护路由

1. 刷新 `/home` 页面
2. 应该仍然显示用户信息（保持登录状态）

### 5. 测试未认证访问

1. 打开浏览器开发者工具
2. 在 Console 中执行: `localStorage.removeItem('token')`
3. 刷新页面
4. 应该跳转到 `/login`

### 6. 手动测试 API

```bash
# 测试登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 测试获取用户信息（替换 YOUR_TOKEN）
curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 测试环境说明

### 默认用户凭据

- 用户名: `admin`
- 密码: `admin123`

### 数据库

- SQLite 数据库位置: `backend/wexion.db`
- 数据库会在后端首次启动时自动初始化

### 端口配置

- 后端 API: `http://localhost:8000`
- 前端应用: `http://localhost:5678`
- API 文档 (Swagger): `http://localhost:8000/docs`

## 常见问题排查

### 后端无法启动

1. 检查 Python 版本: `python --version` (需要 3.13+)
2. 检查依赖安装: `cd backend && uv sync`
3. 检查端口占用: `lsof -i :8000`

### 前端无法启动

1. 检查 Node.js 版本: `node --version` (需要 18+)
2. 检查依赖安装: `cd frontend && pnpm install`
3. 检查端口占用: `lsof -i :5678`

### 登录失败

1. 确认后端服务正在运行
2. 检查浏览器控制台的网络请求
3. 验证用户凭据是否正确
4. 查看后端日志输出

### CORS 错误

如果遇到跨域问题:
1. 确认后端 `app/main.py` 中的 CORS 配置包含前端地址
2. 检查前端 `.env` 文件中的 `VITE_API_BASE_URL` 配置

## 自动化测试

### 单元测试

```bash
cd backend
uv run pytest tests/ -v
```

### 测试覆盖率

```bash
cd backend
uv run pytest tests/ --cov=app --cov-report=html
```

覆盖率报告将生成在 `backend/htmlcov/index.html`

## 性能测试

使用 Apache Bench 进行简单的负载测试:

```bash
# 安装 apache2-utils (如果未安装)
sudo apt-get install apache2-utils

# 测试登录接口 (并发 10, 总请求数 100)
ab -n 100 -c 10 -p login.json -T application/json http://localhost:8000/api/auth/login
```

其中 `login.json` 内容:
```json
{"username": "admin", "password": "admin123"}
```
