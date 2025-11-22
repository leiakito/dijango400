"""
Config package initialization
Ensures Celery app is loaded when Django starts
"""
import pymysql

# 使用 PyMySQL 作为 MySQLdb 的替代
pymysql.install_as_MySQLdb()

from .celery import app as celery_app

__all__ = ('celery_app',)

