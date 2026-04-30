
"""
政策查询模块
"""
from .embedder_query import EmbedderQuery
from ...prompts import PromptManager

RETURN_NUM = 5

class PolicyQuery:
    def __init__(self):
        self.embedder = EmbedderQuery()
        self.prompt_manager = PromptManager()
    
    def _analyze_query_intent(self, user_input, chat_ai, history_messages=None):
        """
        使用中间层AI分析用户的查询意图，确定真正要查询的主题
        """
        intent_prompt = self.prompt_manager.get_policy_query_intent_prompt(user_input, history_messages)
        
        original_system_prompt = chat_ai.system_prompt
        chat_ai.system_prompt = ""
        intent_result = chat_ai.call_chatAI(
            question=intent_prompt,
            history_messages=[],
            token_description="政策查询-意图分析"
        )
        chat_ai.system_prompt = original_system_prompt
        
        # 直接返回分析结果，或者在失败时返回原输入
        return intent_result.strip() if intent_result.strip() else user_input
    
    def query(self, user_input, chat_ai=None, history_messages=None):
        # 如果有chat_ai，先分析意图再查询
        if chat_ai:
            search_query = self._analyze_query_intent(user_input, chat_ai, history_messages)
        else:
            search_query = user_input
            
        results = self.embedder.search(search_query, top_k=RETURN_NUM)
        content = "\n\n".join(results["full_blocks"])
        return content, search_query
    
    def query_with_summary(self, user_input, chat_ai, history_messages=None):
        # 先分析查询意图
        search_query = self._analyze_query_intent(user_input, chat_ai, history_messages)
        
        results = self.embedder.search(search_query, top_k=RETURN_NUM)
        
        small_chunks_content = "\n\n".join(results["small_chunks"])
        full_policy_content = "\n\n".join(results["full_blocks"])
        
        truncated_small_chunks = small_chunks_content[:2000]
        
        summary_prompt = self.prompt_manager.get_policy_summary_prompt(user_input, truncated_small_chunks)
        original_system_prompt = chat_ai.system_prompt
        chat_ai.system_prompt = ""
        summary_generator = chat_ai.call_chatAI_stream(question=summary_prompt, history_messages=[],
                                                          token_description="学生手册查询-内容总结")
        chat_ai.system_prompt = original_system_prompt
        
        return summary_generator, full_policy_content
