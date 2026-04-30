
"""
后端处理模块
处理各类查询逻辑
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from AI_Tool import PolicyQuery


class QueryHandler:
    """查询处理器 - 负责处理各类查询"""
    
    def __init__(self, user_role, account, user_name, policy_query_instance=None):
        if policy_query_instance:
            self.policy_query = policy_query_instance
        else:
            self.policy_query = PolicyQuery()
    
    def handle_policy_query(self, user_input, chat_ai=None, history_messages=None):
        """处理政策查询"""
        content, search_query = self.policy_query.query(user_input, chat_ai, history_messages)
        result = content
        return result, True
    
    def handle_policy_query_with_summary(self, user_input, chat_ai, history_messages=None):
        """处理政策查询并生成AI总结"""
        return self.policy_query.query_with_summary(user_input, chat_ai, history_messages)
