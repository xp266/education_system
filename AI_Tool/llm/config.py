
"""
AI配置管理
"""
import os
import dotenv

# 加载环境变量
dotenv.load_dotenv()

# 全局调试开关
GLOBAL_DEBUG = True

# AI配置
class AIConfig:
    """AI配置类"""
    
    # 从环境变量加载配置
    AI_URL = os.getenv("AI_URL")
    AI_MODEL = os.getenv("AI_MODEL")
    AI_API_KEY = os.getenv("AI_API_KEY")
    
    # 默认参数
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_MAX_TOKENS = 3000
    DEFAULT_THINKING = "disabled"
    DEFAULT_MAX_HISTORY = 5
    TIMEOUT_NORMAL = 30
    TIMEOUT_STREAM = 60

