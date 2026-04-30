
"""
AI_Tool 模块
支持:
- intent: 意图分析
- tools: 工具集（数据库查询、政策查询）
- llm: 大模型交互
- prompts: 提示词管理
"""
from .intent import (
    IntentAnalyzer,
)
from .tools import SmartDatabaseQuery, PolicyQuery, ComplexQuery
from .llm import ChatAI
from .prompts import PromptManager, ContextBuilder

__all__ = [
    # 意图分析
    "IntentAnalyzer",
    # 工具
    "SmartDatabaseQuery",
    "PolicyQuery",
    "ComplexQuery",
    # LLM
    "ChatAI",
    # 提示词管理
    "PromptManager",
    "ContextBuilder"
]

