#!/bin/bash

# 游戏推荐平台 - 开发环境启动脚本

echo "======================================"
echo "  游戏推荐平台 - 开发环境启动"
echo "======================================"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}错误: 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 启动后端
echo -e "${GREEN}[1/2] 启动后端服务...${NC}"
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${RED}错误: 未找到虚拟环境，请先创建虚拟环境${NC}"
    exit 1
fi

# 激活虚拟环境并启动 Django
source venv/bin/activate
echo -e "${YELLOW}后端服务将在 http://localhost:8000 启动${NC}"
python manage.py runserver > /dev/null 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}后端服务已启动 (PID: $BACKEND_PID)${NC}"

# 返回项目根目录
cd ..

# 启动前端
echo -e "${GREEN}[2/2] 启动前端服务...${NC}"
cd frontend

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}正在安装前端依赖...${NC}"
    npm install
fi

echo -e "${YELLOW}前端服务将在 http://localhost:5173 启动${NC}"
npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}前端服务已启动 (PID: $FRONTEND_PID)${NC}"

echo ""
echo -e "${GREEN}======================================"
echo "  所有服务已启动！"
echo "======================================${NC}"
echo ""
echo -e "${YELLOW}访问地址:${NC}"
echo "  前端应用: http://localhost:5173"
echo "  后端 API: http://localhost:8000/api/v1"
echo "  API 文档: http://localhost:8000/api/v1/schema/swagger-ui/"
echo "  管理后台: http://localhost:8000/admin"
echo ""
echo -e "${YELLOW}管理员账户:${NC}"
echo "  用户名: admin"
echo "  密码: admin123456"
echo ""
echo -e "${YELLOW}停止服务:${NC}"
echo "  按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
trap "echo -e '\n${YELLOW}正在停止服务...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo -e '${GREEN}所有服务已停止${NC}'; exit 0" INT

# 保持脚本运行
wait
