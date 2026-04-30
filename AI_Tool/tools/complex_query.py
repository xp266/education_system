
"""
复杂查询模块
同时查询数据库和学生手册
"""
import re
from .database.smart_query import SmartDatabaseQuery
from .policy.policy_queries import PolicyQuery
from ..prompts import PromptManager
from ..prompts import ContextBuilder

class ComplexQuery:
    def __init__(self, user_role='visitor', account='', user_name='', policy_query=None):
        self.user_role = user_role
        self.account = account
        self.user_name = user_name
        self.smart_db = SmartDatabaseQuery(user_role, account, user_name)
        self.policy_query = policy_query if policy_query else PolicyQuery()
        self.prompt_manager = PromptManager()
        self.context_builder = ContextBuilder(max_history_pairs=3)
    
    def _split_query(self, user_input, chat_ai, history_messages=None):
        """
        使用中间层AI将问题拆分为数据库查询词和学生手册查询词
        """
        split_prompt = self.prompt_manager.get_complex_query_split_prompt(user_input, history_messages)
        
        original_system_prompt = chat_ai.system_prompt
        chat_ai.system_prompt = ""
        split_result = chat_ai.call_chatAI(
            question=split_prompt,
            history_messages=[],
            token_description="复杂查询-问题拆分"
        )
        chat_ai.system_prompt = original_system_prompt
        
        # 解析拆分结果
        db_query = user_input  # 默认使用原问题
        policy_query = user_input
        
        # 尝试提取数据库查询词
        db_match = re.search(r'数据库查询词\s*[:：]\s*(.*?)(?=\n|学生手册查询词|$)', split_result)
        if db_match:
            db_query = db_match.group(1).strip()
        
        # 尝试提取学生手册查询词
        policy_match = re.search(r'学生手册查询词\s*[:：]\s*(.*)', split_result)
        if policy_match:
            policy_query = policy_match.group(1).strip()
        
        return db_query, policy_query
    
    def query(self, user_input, chat_ai, history_messages=None):
        """
        复杂查询主函数
        """
        if self.user_role == 'visitor':
            return "请先登录后再查询信息"
        
        # 第一步：使用中间层AI拆分问题（传入历史消息）
        db_query, policy_query = self._split_query(user_input, chat_ai, history_messages)
        
        # 第二步：使用拆分后的查询词查询数据库
        db_result = self.smart_db.query(db_query, chat_ai, history_messages)
        
        # 第三步：使用拆分后的查询词查询学生手册（也传入历史消息）
        policy_content, _ = self.policy_query.query(policy_query, chat_ai, history_messages)
        
        # 第四步：结合两者内容，让AI生成综合回答
        truncated_policy = policy_content[:3000]
        combined_prompt = self.prompt_manager.get_complex_query_prompt(
            user_input, db_result, truncated_policy
        )
        
        original_system_prompt = chat_ai.system_prompt
        chat_ai.system_prompt = ""
        final_answer = chat_ai.call_chatAI(
            question=combined_prompt,
            history_messages=[],
            token_description="复杂查询-综合回答"
        )
        chat_ai.system_prompt = original_system_prompt
        
        return final_answer
    
    def query_with_summary(self, user_input, chat_ai, history_messages=None, status_callback=None):
        """
        复杂查询主函数，带流式输出
        返回 (summary_generator, db_result, policy_content)
        status_callback: 可选的状态回调函数，用于发送状态更新
        """
        if self.user_role == 'visitor':
            return iter(["请先登录后再查询信息"]), None, None
        
        # 状态更新辅助函数
        def update_status(status):
            if status_callback:
                status_callback(status)
        
        # 第一步：使用中间层AI拆分问题（传入历史消息）
        update_status('complex_splitting')
        db_query, policy_query = self._split_query(user_input, chat_ai, history_messages)
        
        # 第二步：使用拆分后的查询词查询数据库
        update_status('complex_db_query')
        db_summary, db_table = self.smart_db.query_with_summary(
            db_query, chat_ai, history_messages
        )
        
        # 收集数据库总结
        db_summary_text = ""
        for chunk in db_summary:
            db_summary_text += chunk
        
        db_result = db_summary_text
        if db_table:
            db_result += "\n\n" + db_table
        
        # 第三步：使用拆分后的查询词查询学生手册（也传入历史消息）
        update_status('complex_policy_query')
        policy_content, _ = self.policy_query.query(policy_query, chat_ai, history_messages)
        
        # 第四步：结合两者内容，让AI生成综合回答
        update_status('complex_combining')
        truncated_policy = policy_content[:3000]
        combined_prompt = self.prompt_manager.get_complex_query_prompt(
            user_input, db_result, truncated_policy
        )
        
        original_system_prompt = chat_ai.system_prompt
        chat_ai.system_prompt = ""
        final_summary_generator = chat_ai.call_chatAI_stream(
            question=combined_prompt,
            history_messages=[],
            token_description="复杂查询-综合回答"
        )
        chat_ai.system_prompt = original_system_prompt
        
        return final_summary_generator, db_result, policy_content

