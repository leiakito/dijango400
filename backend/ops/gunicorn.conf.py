"""
Gunicorn 配置文件
"""
import multiprocessing

# 绑定地址
bind = "0.0.0.0:8000"

# Worker 进程数
workers = multiprocessing.cpu_count() * 2 + 1

# Worker 类型
worker_class = "sync"

# 每个 worker 的线程数
threads = 2

# 超时时间
timeout = 60

# 保持连接时间
keepalive = 5

# 最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50

# 日志
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"

# 进程名称
proc_name = "game_platform"

# 守护进程
daemon = False

# PID 文件
pidfile = "logs/gunicorn.pid"

