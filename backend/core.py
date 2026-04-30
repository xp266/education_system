
"""
后端核心模块
智能助手主逻辑
"""
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from AI_Tool import (
    IntentAnalyzer,
    ChatAI,
    SmartDatabaseQuery,
    PromptManager,
    PolicyQuery,
    ComplexQuery
)
from AI_Tool.utils import TokenTracker
from utils import strip_markdown
from handlers import QueryHandler
import database


class EducationAssistant:
    """教育智能助手核心类"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.prompt_manager = PromptManager()
        
        # 初始化意图分析器（先不传入token_tracker，在每次查询时动态传入）
        self.first_analyzer_intent_template = self.prompt_manager._first_intent_prompt
        
        # 初始化聊天AI
        self.chat_ai_system_prompt = self.prompt_manager.get_chat_system_prompt()
        
        # 初始化政策查询实例（单例模式，避免每次查询都重新加载）
        self.policy_query = PolicyQuery()
    
    def preload(self):
        """启动预加载：加载模型和索引"""
        print("[EducationAssistant] 开始系统预加载...")
        # 模拟调用一次政策查询，强制初始化所有内容
        try:
            self.policy_query.query("测试")
        except Exception as e:
            print(f"[EducationAssistant] 模拟查询时出现错误（不影响使用）: {e}")
        print("[EducationAssistant] 系统预加载完成")
    
    def _load_history_messages(self, user_role, conversation_id, guest_history):
        """加载历史消息 - 获取最近3个消息对（6条消息），保证上下文完整"""
        history_messages = []
        
        if user_role == 'visitor' and guest_history is not None:
            history_messages = [
                {'role': msg['role'], 'content': strip_markdown(msg['content'])}
                for msg in guest_history
            ]
            if len(history_messages) > 6:
                start_idx = len(history_messages) - 6
                if start_idx % 2 != 0:
                    start_idx += 1
                history_messages = history_messages[start_idx:]
        
        elif conversation_id:
            db_messages = database.get_messages(conversation_id, limit=100)
            history_messages = [
                {'role': msg['role'], 'content': strip_markdown(msg['content'])}
                for msg in db_messages
            ]
            if len(history_messages) > 6:
                start_idx = len(history_messages) - 6
                if start_idx % 2 != 0:
                    start_idx += 1
                history_messages = history_messages[start_idx:]
        
        return history_messages
    
    def _get_or_create_conversation(self, user_role, account, conversation_id):
        if conversation_id is None and user_role != 'visitor':
            latest_conv = database.get_latest_conversation(account)
            if latest_conv:
                conversation_id = latest_conv['conversation_id']
            else:
                conversation_id = database.create_conversation(account, user_role)
        return conversation_id
    
    def _generate_conversation_title(self, user_input, chat_ai=None, token_tracker=None):
        try:
            prompt = self.prompt_manager.get_title_generation_prompt(user_input)
            title = chat_ai.call_chatAI(question=prompt, history_messages=[], debug=self.debug,
                                       token_description="对话标题生成")
            title = title.strip()[:10]
            if not title:
                title = '新对话'
            return title
        except:
            return '新对话'
    
    def _save_conversation(self, conversation_id, user_role, user_input, ai_response, is_first_message, chat_ai=None, token_tracker=None):
        if conversation_id and user_role != 'visitor':
            database.add_message(conversation_id, 'user', user_input)
            database.add_message(conversation_id, 'assistant', ai_response)
            
            if is_first_message and chat_ai:
                title = self._generate_conversation_title(user_input, chat_ai, token_tracker)
                database.update_conversation_title(conversation_id, title)
    
    def process_query(self, user_input, user_role='visitor', account='', user_name='', 
                    conversation_id=None, guest_history=None):
        conversation_id = self._get_or_create_conversation(user_role, account, conversation_id)
        history_messages = self._load_history_messages(user_role, conversation_id, guest_history)
        
        is_first_message = False
        if conversation_id and user_role != 'visitor' and len(history_messages) == 0:
            is_first_message = True
        
        # 初始化token追踪器
        token_tracker = TokenTracker()
        
        # 初始化带token追踪的意图分析器
        first_analyzer = IntentAnalyzer(
            system_prompt_template=self.first_analyzer_intent_template,
            token_tracker=token_tracker
        )
        
        # 初始化带token追踪的聊天AI
        chat_ai = ChatAI(
            system_prompt=self.chat_ai_system_prompt,
            token_tracker=token_tracker
        )
        
        # 传入预加载的 policy_query 实例
        query_handler = QueryHandler(user_role, account, user_name, self.policy_query)
        first_intent = first_analyzer.analyze_intent(user_input, user_role=user_role, 
                                                         user_name=user_name, 
                                                         history_messages=history_messages, 
                                                         debug=self.debug)
        
        result = ""
        is_policy = False
        
        if "复杂查询" in first_intent:
            complex_query = ComplexQuery(user_role, account, user_name, self.policy_query)
            result = complex_query.query(user_input, chat_ai, history_messages)
        
        elif "数据库查询" in first_intent:
            smart_db = SmartDatabaseQuery(user_role, account, user_name)
            result = smart_db.query(user_input, chat_ai, history_messages)
        
        elif "学生手册查询" in first_intent or "学生手册" in first_intent:
            result, is_policy = query_handler.handle_policy_query(user_input, chat_ai, history_messages)
        
        else:
            result = chat_ai.call_chatAI(question=user_input, history_messages=history_messages, 
                                           debug=self.debug, use_full_context=True,
                                           token_description="主对话")
        
        self._save_conversation(conversation_id, user_role, user_input, result, is_first_message, chat_ai, token_tracker)
        
        # 打印token消耗总结
        token_tracker.print_summary()
        
        return {
            'response': result,
            'conversation_id': conversation_id,
            'is_policy': is_policy
        }
    
    def process_query_stream(self, user_input, user_role='visitor', account='', user_name='', 
                           conversation_id=None, guest_history=None):
        conversation_id = self._get_or_create_conversation(user_role, account, conversation_id)
        history_messages = self._load_history_messages(user_role, conversation_id, guest_history)
        
        is_first_message = False
        if conversation_id and user_role != 'visitor' and len(history_messages) == 0:
            is_first_message = True
        
        # 初始化token追踪器
        token_tracker = TokenTracker()
        
        # 初始化带token追踪的意图分析器
        first_analyzer = IntentAnalyzer(
            system_prompt_template=self.first_analyzer_intent_template,
            token_tracker=token_tracker
        )
        
        # 初始化带token追踪的聊天AI
        chat_ai = ChatAI(
            system_prompt=self.chat_ai_system_prompt,
            token_tracker=token_tracker
        )
        
        # 传入预加载的 policy_query 实例
        query_handler = QueryHandler(user_role, account, user_name, self.policy_query)
        
        # 首先发送"思考中"状态
        yield {'type': 'status', 'status': 'thinking'}
        
        first_intent = first_analyzer.analyze_intent(user_input, user_role=user_role, 
                                                         user_name=user_name, 
                                                         history_messages=history_messages, 
                                                         debug=self.debug)
        
        is_policy = False
        final_response = ""
        
        if "复杂查询" in first_intent:
            # 1. 开始复杂查询
            yield {'type': 'status', 'status': 'complex_analyzing'}
            complex_query = ComplexQuery(user_role, account, user_name, self.policy_query)
            
            # 2. 正在拆分问题
            yield {'type': 'status', 'status': 'complex_splitting'}
            
            # 3. 正在查询数据库
            yield {'type': 'status', 'status': 'complex_querying_db'}
            
            # 获取复杂查询结果
            summary_generator, db_result, policy_content = complex_query.query_with_summary(
                user_input, chat_ai, history_messages
            )
            
            # 4. 正在查询政策
            yield {'type': 'status', 'status': 'complex_querying_policy'}
            
            # 5. 正在生成综合回答
            yield {'type': 'status', 'status': 'complex_generating'}
            
            # 流式输出AI综合总结
            for chunk in summary_generator:
                final_response += chunk
                yield {'type': 'content', 'data': chunk, 'is_policy': is_policy}
            
            # 添加分隔文字
            separator_text = "\n\n以上是综合回答，如需查看详细数据可点击下方："
            final_response += separator_text
            yield {'type': 'content', 'data': separator_text, 'is_policy': is_policy}
            
            # 添加可点击的数据库详细数据
            view_db_detail_html = f'\n\n<div class="view-detail-btn" onclick="showPolicyDetail(`{db_result.replace("`", "\\`").replace("\n", "\\n")}`)">查看详细数据</div>'
            yield {'type': 'content', 'data': view_db_detail_html, 'is_policy': is_policy}
            
            # 添加可点击的政策详细内容
            view_policy_detail_html = f'\n\n<div class="view-detail-btn" onclick="showPolicyDetail(`{policy_content.replace("`", "\\`").replace("\n", "\\n")}`)">查看相关政策</div>'
            yield {'type': 'content', 'data': view_policy_detail_html, 'is_policy': is_policy}
        
        elif "数据库查询" in first_intent:
            # 切换状态为查询数据库
            yield {'type': 'status', 'status': 'querying_db'}
            smart_db = SmartDatabaseQuery(user_role, account, user_name)
            # 获取数据库查询结果，包含表格和总结
            summary, table = smart_db.query_with_summary(user_input, chat_ai, history_messages)
            
            # 流式输出AI总结
            for chunk in summary:
                final_response += chunk
                yield {'type': 'content', 'data': chunk, 'is_policy': is_policy}
            
            # 只有当有表格时才添加分隔文字和表格
            if table is not None:
                # 添加分隔文字
                separator_text = "\n\n以上内容是我根据部分表格进行的总结，表格如下：\n\n"
                final_response += separator_text
                yield {'type': 'content', 'data': separator_text, 'is_policy': is_policy}
                
                # 添加表格
                final_response += table
                yield {'type': 'content', 'data': table, 'is_policy': is_policy}
        
        elif "学生手册查询" in first_intent or "学生手册" in first_intent:
            # 切换状态为查询政策
            yield {'type': 'status', 'status': 'querying_policy'}
            # 获取政策查询结果：(summary_generator, full_policy_content)
            summary_generator, full_policy_content = query_handler.handle_policy_query_with_summary(user_input, chat_ai, history_messages)
            
            # 流式输出AI总结
            for chunk in summary_generator:
                final_response += chunk
                yield {'type': 'content', 'data': chunk, 'is_policy': is_policy}
            
            # 添加分隔文字
            separator_text = "\n\n以上内容是我根据学生手册的部分内容总结得到，如需要详细内容，可点击下方查看详细内容："
            final_response += separator_text
            yield {'type': 'content', 'data': separator_text, 'is_policy': is_policy}
            
            # 添加可点击的控件
            # 注意：保存到数据库时只保存final_response（总结部分）
            view_detail_html = f'\n\n<div class="view-detail-btn" onclick="showPolicyDetail(`{full_policy_content.replace("`", "\\`").replace("\n", "\\n")}`)">查看详细内容</div>'
            yield {'type': 'content', 'data': view_detail_html, 'is_policy': is_policy}
        
        else:
            for chunk in chat_ai.call_chatAI_stream(question=user_input, history_messages=history_messages, 
                                                      debug=self.debug, use_full_context=True,
                                                      token_description="主对话"):
                final_response += chunk
                yield {'type': 'content', 'data': chunk, 'is_policy': is_policy}
        
        self._save_conversation(conversation_id, user_role, user_input, final_response, is_first_message, chat_ai, token_tracker)
        
        # 打印token消耗总结
        token_tracker.print_summary()
        
        yield {'type': 'done', 'conversation_id': conversation_id}

