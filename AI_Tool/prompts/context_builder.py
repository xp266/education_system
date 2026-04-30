

"""
上下文拼接类
提供两种上下文构建方式：
1. 提取最近n对完整消息（包括用户和AI）
2. 仅提取最近n对消息中的用户消息
"""


class ContextBuilder:
    """上下文构建器"""
    
    def __init__(self, max_history_pairs=3):
        """
        初始化
        
        Args:
            max_history_pairs: 最多保留多少对历史消息（每对包含用户+AI）
        """
        self.max_history_pairs = max_history_pairs
    
    def build_full_context(self, history_messages, max_pairs=None):
        """
        构建完整上下文 - 包含最近n对用户和AI的完整消息
        
        Args:
            history_messages: 历史消息列表，格式为 [{'role': 'user', 'content': '...'}, ...]
            max_pairs: 最多保留的消息对数，默认使用初始化时的max_history_pairs
            
        Returns:
            完整上下文消息列表
        """
        actual_max_pairs = max_pairs or self.max_history_pairs
        max_messages = actual_max_pairs * 2
        
        # 截断到最近的max_messages条消息
        if len(history_messages) > max_messages:
            start_idx = len(history_messages) - max_messages
            # 确保从用户消息开始（如果总数是奇数）
            if start_idx % 2 != 0:
                start_idx += 1
            context = history_messages[start_idx:]
        else:
            context = history_messages
        
        return [{'role': msg['role'], 'content': msg['content']} for msg in context]
    
    def build_user_only_context(self, history_messages, max_pairs=None):
        """
        构建仅用户消息的上下文 - 格式为"用户输入：xxxx AI已回答"
        
        Args:
            history_messages: 历史消息列表，格式为 [{'role': 'user', 'content': '...'}, ...]
            max_pairs: 最多保留的消息对数，默认使用初始化时的max_history_pairs
            
        Returns:
            仅用户消息的上下文列表，每条都是用户消息加"AI已回答"标记
        """
        actual_max_pairs = max_pairs or self.max_history_pairs
        
        # 提取所有用户消息
        user_messages = []
        for msg in history_messages:
            if msg['role'] == 'user':
                user_messages.append(msg['content'])
        
        # 取最近的n条用户消息
        if len(user_messages) > actual_max_pairs:
            user_messages = user_messages[-actual_max_pairs:]
        
        # 构建上下文
        context = []
        for user_input in user_messages:
            context.append({'role': 'user', 'content': f'用户输入：{user_input} 【AI已回答】'})
        
        return context

