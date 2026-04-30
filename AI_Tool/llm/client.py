
"""
AI客户端 - 负责与AI API进行交互
"""
import requests
import json
from .config import AIConfig, GLOBAL_DEBUG


class AIClient:
    """AI客户端 - 负责发送请求和接收响应"""
    
    def __init__(self, config=None):
        self.config = config or AIConfig()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.AI_API_KEY}"
        }
    
    def _build_payload(self, messages, temperature=None, max_tokens=None, 
                      thinking=None, stream=False):
        """构建请求payload"""
        return {
            "model": self.config.AI_MODEL,
            "messages": messages,
            "temperature": temperature or self.config.DEFAULT_TEMPERATURE,
            "max_tokens": max_tokens or self.config.DEFAULT_MAX_TOKENS,
            "thinking": {"type": thinking or self.config.DEFAULT_THINKING},
            "stream": stream,
            "stream_options": {"include_usage": True} if stream else None
        }
    
    def call_normal(self, messages, temperature=None, max_tokens=None, thinking=None, debug=False):
        """调用非流式AI"""
        
        payload = self._build_payload(messages, temperature, max_tokens, thinking, stream=False)
        
        try:
            response = requests.post(
                url=self.config.AI_URL,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=self.config.TIMEOUT_NORMAL
            )
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            print(f"错误: {str(e)}")
            return None
    
    def call_stream(self, messages, temperature=None, max_tokens=None, thinking=None, debug=False):
        """调用流式AI，返回生成器"""

        payload = self._build_payload(messages, temperature, max_tokens, thinking, stream=True)
        
        try:
            response = requests.post(
                url=self.config.AI_URL,
                headers=self.headers,
                data=json.dumps(payload),
                stream=True,
                timeout=self.config.TIMEOUT_STREAM
            )
            response.raise_for_status()
            return response
        
        except Exception as e:
            print(f"错误: {str(e)}")
            return None

