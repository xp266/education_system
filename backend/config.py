
"""
后端配置文件
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Flask 配置
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-12345')
DEBUG = True
HOST = os.getenv('BACKEND_HOST', '0.0.0.0')
PORT = int(os.getenv('BACKEND_PORT', 5001))
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5000')

# 数据库配置
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'education_system')
DB_CHARSET = 'utf8mb4'
