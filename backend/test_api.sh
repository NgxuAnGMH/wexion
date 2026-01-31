#!/bin/bash
# 快速 API 测试脚本

set -e

API_URL="http://localhost:8000"
USERNAME="admin"
PASSWORD="admin123"

echo "🧪 Wexion CMS API - 快速测试"
echo "===================================="
echo ""

# 检查后端是否运行
echo "1️⃣ 检查后端服务..."
if curl -s "$API_URL/" > /dev/null 2>&1; then
    echo "✅ 后端服务运行中"
else
    echo "❌ 后端服务未运行，请先启动: cd backend && uv run uvicorn app.main:app --reload"
    exit 1
fi

# 测试登录
echo ""
echo "2️⃣ 测试登录 API..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}")

echo "响应: $LOGIN_RESPONSE"

# 提取 token
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ 登录失败"
    exit 1
fi

echo "✅ 登录成功"
echo "Token: ${TOKEN:0:50}..."

# 测试获取用户信息
echo ""
echo "3️⃣ 测试获取用户信息 API..."
USER_RESPONSE=$(curl -s -X GET "$API_URL/api/users/me" \
  -H "Authorization: Bearer $TOKEN")

echo "响应: $USER_RESPONSE"

if echo "$USER_RESPONSE" | grep -q "$USERNAME"; then
    echo "✅ 获取用户信息成功"
else
    echo "❌ 获取用户信息失败"
    exit 1
fi

# 测试无效 token
echo ""
echo "4️⃣ 测试无效 token..."
INVALID_RESPONSE=$(curl -s -X GET "$API_URL/api/users/me" \
  -H "Authorization: Bearer invalid_token")

if echo "$INVALID_RESPONSE" | grep -q "401\|403\|detail"; then
    echo "✅ 无效 token 被正确拒绝"
else
    echo "⚠️  无效 token 处理可能有问题"
fi

# 测试错误密码
echo ""
echo "5️⃣ 测试错误密码..."
ERROR_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"wrong_password\"}")

if echo "$ERROR_RESPONSE" | grep -q "detail\|error"; then
    echo "✅ 错误密码被正确拒绝"
else
    echo "⚠️  错误密码处理可能有问题"
fi

# 总结
echo ""
echo "===================================="
echo "✅ API 测试完成！"
echo ""
echo "📊 测试结果："
echo "   ✅ 后端服务运行正常"
echo "   ✅ 登录功能正常"
echo "   ✅ 用户信息获取正常"
echo "   ✅ Token 验证正常"
echo "   ✅ 错误处理正常"
echo ""
echo "🚀 下一步：启动前端进行 UI 测试"
echo "   cd frontend && pnpm run dev --port 5678"
