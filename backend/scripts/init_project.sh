#!/bin/bash
# 项目初始化脚本

echo "=== 游戏推荐平台后端初始化 ==="

# 检查 Python 版本
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

# 创建虚拟环境（可选）
# python -m venv venv
# source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 复制环境变量文件
if [ ! -f .env ]; then
    echo "复制环境变量配置..."
    cp .env.example .env
    echo "请编辑 .env 文件配置数据库等信息"
fi

# 创建必要的目录
echo "创建目录..."
mkdir -p logs media static backups

# 数据库迁移
echo "执行数据库迁移..."
python manage.py makemigrations
python manage.py migrate

# 创建超级用户（可选）
echo "是否创建超级用户？(y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ]; then
    python manage.py createsuperuser
fi

# 收集静态文件
echo "收集静态文件..."
python manage.py collectstatic --noinput

echo ""
echo "=== 初始化完成 ==="
echo "启动开发服务器: python manage.py runserver"
echo "启动 Celery Worker: celery -A config worker -l info"
echo "启动 Celery Beat: celery -A config beat -l info"
echo "API 文档: http://localhost:8000/api/schema/swagger/"

