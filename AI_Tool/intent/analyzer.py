
"""
意图分析器
提供各类意图分析功能
"""
from ..llm import ChatAI
from ..utils import TokenTracker
from ..prompts import ContextBuilder


class IntentAnalyzer:
    """意图分析器 - 用于分析用户输入的意图"""
    
    def __init__(self, system_prompt_template=None, temperature=0.1, max_tokens=50, token_tracker=None):
        # 初始化 AI 调用类
        self.system_prompt_template = system_prompt_template
        self.chatAI = ChatAI(system_prompt=system_prompt_template or "", token_tracker=token_tracker)
        # 初始化上下文构建器
        self.context_builder = ContextBuilder(max_history_pairs=3)
        # 角色映射字典
        self.role_mapping = {
            'visitor': '访客',
            'student': '学生',
            'teacher': '教师'
        }
        # Token追踪器
        self.token_tracker = token_tracker

    def analyze_intent(self, user_input, user_role='visitor', user_name='', history_messages=None, debug=False):
        """
        分析用户输入的意图，只返回意图
        :param user_input: 用户输入
        :param user_role: 用户角色
        :param user_name: 用户姓名
        :param history_messages: 历史消息列表
        :param debug: 是否调试
        """
        if not user_input or len(user_input.strip()) == 0:
            return "输入为空"

        try:
            # 动态构建系统提示词
            system_prompt = self.system_prompt_template
            if system_prompt:
                user_role_cn = self.role_mapping.get(user_role, user_role)
                
                # 构建历史消息字符串（仅用户消息）
                history_str = ""
                if history_messages:
                    user_context = self.context_builder.build_user_only_context(history_messages)
                    history_str = "\n".join([msg['content'] for msg in user_context])
                
                # 处理提示词中的所有可能的占位符
                format_kwargs = {
                    'user_role': user_role,
                    'user_role_cn': user_role_cn,
                    'user_name': user_name,
                    'user_input': user_input,
                    'history_messages': history_str
                }
                system_prompt = system_prompt.format(**format_kwargs)
                # 更新 chatAI 的系统提示词
                self.chatAI.system_prompt = system_prompt
            
            # 调用 AI 分析(已经使用了提示词构造，不需要再输入问题)
            intent = self.chatAI.call_chatAI(
                question=" ",
                debug=debug,
                token_description="意图分析"
            )
            return intent.strip()
        
        except Exception as e:
            return f"意图分析失败: {str(e)}"


