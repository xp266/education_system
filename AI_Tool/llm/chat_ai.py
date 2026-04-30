
"""
ChatAI类 - 提供对话功能
"""
import json
from .client import AIClient
from .config import AIConfig, GLOBAL_DEBUG
from ..utils import TokenTracker
from ..prompts import ContextBuilder


class ChatAI:
    """ChatAI类 - 提供对话功能，包含非流式和流式调用"""
    
    def __init__(self, system_prompt=None, temperature=None, max_tokens=None, 
                thinking=None, max_history=None, token_tracker=None):
        # 配置
        self.config = AIConfig()
        self.system_prompt = system_prompt
        self.temperature = temperature or self.config.DEFAULT_TEMPERATURE
        self.max_tokens = max_tokens or self.config.DEFAULT_MAX_TOKENS
        self.thinking = thinking or self.config.DEFAULT_THINKING
        self.max_history = max_history or self.config.DEFAULT_MAX_HISTORY
        
        # 初始化上下文构建器
        # 计算消息对数量：每对包含user+assistant两条
        if self.max_history > 0:
            max_pairs = self.max_history // 2
        else:
            max_pairs = 3
        self.context_builder = ContextBuilder(max_history_pairs=max_pairs)
        
        # 初始化客户端
        self.client = AIClient(self.config)
        
        # 累计token消耗
        self.total_tokens_used = 0
        
        # Token追踪器
        self.token_tracker = token_tracker
    
    def _build_messages(self, question, history_messages=None, use_full_context=False):
        """构造上下文消息列表
            question: 本次提问
            history_messages: 历史消息列表
            use_full_context: 是否使用完整消息对（用户+AI回复），False 表示仅用户消息
        """
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        
        if history_messages:
            if use_full_context:
                # 使用完整消息对
                full_context = self.context_builder.build_full_context(history_messages)
                for msg in full_context:
                    messages.append(msg)

            else:
                # 使用仅用户消息的上下文
                user_context = self.context_builder.build_user_only_context(history_messages)
                for msg in user_context:
                    messages.append(msg)

        messages.append({"role": "user", "content": question})
        
        return messages
    
    def call_chatAI(self, question, history_messages=None, debug=False, use_full_context=False, token_description=""):
        """
        调用AI对话（非流式）
        
        :param token_description: 本次调用的描述，用于token追踪
        """
        actual_debug = debug or GLOBAL_DEBUG
        messages = self._build_messages(question, history_messages, use_full_context)
        
        result = self.client.call_normal(
            messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            thinking=self.thinking,
            debug=debug
        )
        
        if not result:
            return "抱歉，发生了一点问题，请稍后再试！"
        
        # 解析响应
        tokens = result["usage"]["total_tokens"]
        self.total_tokens_used += tokens
        ai_reply = result["choices"][0]["message"]["content"]
        
        # 如果有token追踪器，记录本次消耗
        if self.token_tracker:
            self.token_tracker.add_tokens(tokens, token_description or "AI调用")
        
        if actual_debug:
            print(f"\n[DEBUG] 非流式AI实际接收的完整上下文:")
            print(f"{'-'*80}")
            for idx, msg in enumerate(messages, 1):
                role = msg["role"]
                content = msg["content"]
                print(f"{idx}. [{role}]")
                print(f"{content}")
                print(f"{'-'*80}")
            print(f"\n[DEBUG] AI回复:")
            print(f"{ai_reply}")
            print(f"{'='*80}\n")
        
        return ai_reply
    
    def call_chatAI_stream(self, question, history_messages=None, debug=False, use_full_context=False, token_description=""):
        """
        调用AI对话（流式）
        返回生成器，逐个返回文本块
        
        :param token_description: 本次调用的描述，用于token追踪
        """
        actual_debug = debug or GLOBAL_DEBUG
        messages = self._build_messages(question, history_messages, use_full_context)
        
        response = self.client.call_stream(
            messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            thinking=self.thinking,
            debug=debug
        )
        
        if not response:
            yield "抱歉，发生了一点问题，请稍后再试！"
            return
        
        full_response = ""
        tokens_used = 0
        
        try:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            # 检查是否有usage信息
                            if 'usage' in data and data['usage']:
                                tokens_used = data['usage'].get('total_tokens', 0)
                                if tokens_used:
                                    self.total_tokens_used += tokens_used
                                    # 如果有token追踪器，记录本次消耗
                                    if self.token_tracker:
                                        self.token_tracker.add_tokens(tokens_used, token_description or "流式AI调用")
                            # 处理内容
                            has_choices = 'choices' in data
                            choices_not_empty = len(data['choices']) > 0 if has_choices else False
                            if has_choices and choices_not_empty:
                                delta = data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    full_response += content
                                    yield content
                        except json.JSONDecodeError:
                            continue
            
            if actual_debug:
                print(f"\n[DEBUG] 流式AI实际接收的完整上下文:")
                print(f"{'-'*80}")
                for idx, msg in enumerate(messages, 1):
                    role = msg["role"]
                    content = msg["content"]
                    print(f"{idx}. [{role}]")
                    print(f"{content}")
                    print(f"{'-'*80}")
                print(f"\n[DEBUG] AI完整回复:")
                print(f"{full_response}")
                print(f"{'='*80}\n")
            
        except Exception as e:
            print(f"错误: {str(e)}")
            yield "抱歉，发生了一点问题，请稍后再试！"

