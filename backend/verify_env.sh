#!/bin/bash
# 环境验证脚本

set -e

echo "🔍 Wexion CMS 认证系统 - 环境验证"
echo "===================================="
echo ""

# 检查 Python 版本
echo "📦 检查 Python 版本..."
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "✅ Python: $PYTHON_VERSION"
else
    echo "❌ Python 未安装"
    exit 1
fi

# 检查 uv
echo ""
echo "📦 检查 uv 包管理器..."
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    echo "✅ uv: $UV_VERSION"
else
    echo "❌ uv 未安装"
    exit 1
fi

# 检查 Node.js
echo ""
echo "📦 检查 Node.js 版本..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js: $NODE_VERSION"
else
    echo "❌ Node.js 未安装"
    exit 1
fi

# 检查 pnpm
echo ""
echo "📦 检查 pnpm..."
if command -v pnpm &> /dev/null; then
    PNPM_VERSION=$(pnpm --version)
    echo "✅ pnpm: $PNPM_VERSION"
else
    echo "❌ pnpm 未安装"
    exit 1
fi

# 检查后端依赖
echo ""
echo "📦 检查后端依赖..."
BACKEND_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -d "$BACKEND_DIR/.venv" ]; then
    echo "✅ 后端虚拟环境存在"
else
    echo "❌ 后端虚拟环境不存在，请运行: cd backend && uv sync"
    exit 1
fi

# 检查前端依赖
echo ""
echo "📦 检查前端依赖..."
FRONTEND_DIR="$(dirname "$BACKEND_DIR")/frontend"
if [ -d "$FRONTEND_DIR/node_modules" ]; then
    echo "✅ 前端依赖已安装"
else
    echo "❌ 前端依赖不存在，请运行: cd frontend && pnpm install"
    exit 1
fi

# 检查数据库
echo ""
echo "📦 检查数据库..."
if [ -f "$BACKEND_DIR/wexion.db" ]; then
    echo "✅ 数据库文件存在"
    DB_SIZE=$(du -h "$BACKEND_DIR/wexion.db" | cut -f1)
    echo "   大小: $DB_SIZE"
else
    echo "⚠️  数据库文件不存在（将在首次启动时创建）"
fi

# 检查端口占用
echo ""
echo "🔍 检查端口占用..."

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口 8000 已被占用"
else
    echo "✅ 端口 8000 可用"
fi

if lsof -Pi :5678 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口 5678 已被占用"
else
    echo "✅ 端口 5678 可用"
fi

# 检查配置文件
echo ""
echo "📝 检查配置文件..."

if [ -f "$BACKEND_DIR/config.yaml" ]; then
    echo "✅ 后端配置文件存在"
else
    echo "❌ 后端配置文件不存在"
    exit 1
fi

# 总结
echo ""
echo "===================================="
echo "✅ 环境验证完成！"
echo ""
echo "🚀 下一步："
echo "   1. 启动后端: cd backend && uv run uvicorn app.main:app --reload --port 8000"
echo "   2. 启动前端: cd frontend && pnpm run dev --port 5678"
echo "   3. 访问应用: http://localhost:5678"
echo ""
echo "📖 详细测试说明请查看: backend/TESTING.md"
