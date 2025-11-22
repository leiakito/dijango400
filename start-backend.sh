#!/bin/bash

# 启动Django后端服务器
cd /Volumes/GT/dijango400/backend

# 激活虚拟环境
source venv/bin/activate

# 设置开发环境
export DJANGO_SETTINGS_MODULE=config.settings.dev

# 检查MySQL是否运行
echo "检查MySQL服务..."
if ! mysql -u root -e "SELECT 1" > /dev/null 2>&1; then
    echo "错误: MySQL服务未运行，请先启动MySQL"
    echo "可以使用: brew services start mysql"
    exit 1
fi

# 运行迁移
echo "执行数据库迁移..."
python manage.py migrate

# 启动服务器
echo "启动Django开发服务器..."
python manage.py runserver 8000

