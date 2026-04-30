
"""
Backend 业务逻辑服务器
端口：5001
"""
from flask import Flask
from flask_cors import CORS
from config import SECRET_KEY, HOST, PORT, FRONTEND_URL, DEBUG
from core import EducationAssistant
from routes import register_routes
import os


def create_app(preload=True):
    """创建 Flask 应用实例"""
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    # 本地开发环境，不用 SameSite=None
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False
    # 允许所有来源（因为前端会代理请求）
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    
    # 初始化助手
    assistant = EducationAssistant(debug=DEBUG)
    
    # 注册路由
    register_routes(app, assistant)
    
    if preload:
        # 预加载模型和索引
        assistant.preload()
    
    return app

if __name__ == '__main__':
    # 检查是否是 Werkzeug 的重载器进程
    is_worker_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    app = create_app(preload=is_worker_process)
    app.run(debug=DEBUG, host=HOST, port=PORT)
