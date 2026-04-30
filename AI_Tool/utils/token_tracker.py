
"""
Token追踪器
用于追踪单次对话的所有token消耗
"""


class TokenTracker:
    """Token追踪器 - 追踪单次对话的所有token消耗"""
    
    def __init__(self):
        self.total_tokens = 0
        self.records = []  # 记录每次调用的详情
    
    def add_tokens(self, tokens, description=""):
        """
        添加token消耗记录
        
        :param tokens: 本次消耗的token数
        :param description: 本次调用的描述（如"意图分析"、"主对话"等）
        """
        self.total_tokens += tokens
        self.records.append({
            "tokens": tokens,
            "description": description,
            "total_after": self.total_tokens
        })
    
    def get_total(self):
        """获取总token消耗"""
        return self.total_tokens
    
    def get_records(self):
        """获取详细记录"""
        return self.records
    
    def print_summary(self):
        """打印token消耗总结"""
        print("\n" + "=" * 80)
        print("【对话Token消耗总结】")
        print("=" * 80)
        for i, record in enumerate(self.records, 1):
            print(f"{i}. {record['description']}: {record['tokens']} tokens")
        print("-" * 80)
        print(f"本次对话总Token消耗: {self.total_tokens} tokens")
        print("=" * 80 + "\n")
    
    def reset(self):
        """重置追踪器"""
        self.total_tokens = 0
        self.records = []

