
"""
提示词管理器
集中管理所有AI提示词
"""


class PromptManager:
    """提示词管理器"""
    
    def __init__(self):
        """初始化提示词"""
        # 第一层意图分析提示词
        self._first_intent_prompt = """
分析用户本次想要了解的内容，部分情况可能需要根据历史消息判断
为了获取真实内容，需要执行以下什么操作。
分类:
- 数据库查询: 可以查到学生，专业，学院，教师，成绩等信息
- 学生手册查询: 能够找到学校简介，转专业，学生规定等政策信息或学校信息
- 复杂查询: 可能需要同时查询数据库和学生手册才能回答的问题，如绩点是否满足毕业要求
- 普通对话: 聊天，抱怨，提问等
输出: 只返回分类名

历史消息:{history_messages}

本次输入: {user_input}
"""


        # 数据库查询权限确认提示词
        self._permission_check_prompt = """
历史消息:
{history_messages}

本次提问: {user_input}

当前用户身份: {user_role_cn}
当前用户姓名: {user_name}

权限规则:
- 访客: 无权查询
- 学生: 只能查自己或学校相关的信息，不能查其他学生的信息
- 教师: 可查询学生和自己以及学校相关的信息

判断权限，部分情况可能需要根据历史消息判断。
只回答"是"或"否"
"""
        
        # 聊天系统提示词
        self._chat_system_prompt = """
你是教育系统智能助手，能查询教务数据和学校政策，所有回答要基于事实，简洁回答用户问题。
"""
        
        # 对话标题生成提示词
        self._title_generation_prompt = """
为用户提问生成标题，不超过10字，只返回标题。
用户提问: {user_input}
"""
        
        # 智能数据库查询提示词模板
        self._smart_query_prompt = """
历史消息:
{history_messages}

本次提问: {user_input}

表结构:
{table_structure}

{permission_condition}

要求:
根据用户的本次提问和身份生成SQL语句，若用户没有要求查询多少，就限制最多输出10条数据。
只返回SELECT SQL语句，不要任何注释和占位符,用```sql包裹
"""
        
        # 学生表结构
        self._student_tables = """
students(student_id, student_no, student_name, gender, phone, major_id, class_id)
majors(major_id, major_code, major_name, department(学院), degree_type(学位类型), duration(学制))
classes(class_id, class_name, grade(年级), major_id, head_teacher_id(班主任id), student_count)
courses(course_id, course_code, course_name, credits, hours(学时), course_type)
course_teachings(teaching_id, course_id, teacher_id, semester, classroom, schedule)
course_selections(selection_id, student_id, teaching_id)
scores(score_id, student_id, teaching_id, usual_score, final_score, total_score, grade_point, semester)
teachers(teacher_id, teacher_no, teacher_name, title, department(学院))
"""
        
        # 教师表结构
        self._teacher_tables = """
students(student_id, student_no, student_name, gender, phone, major_id, class_id)
majors(major_id, major_code, major_name, department(学院), degree_type(学位类型), duration(学制))
classes(class_id, class_name, grade(年级), major_id, head_teacher_id(班主任id), student_count)
courses(course_id, course_code, course_name, credits, hours(学时), course_type)
course_teachings(teaching_id, course_id, teacher_id, semester(学期), classroom, schedule)
course_selections(selection_id, student_id, teaching_id)
scores(score_id, student_id, teaching_id, usual_score, final_score, total_score, grade_point, semester)
teachers(teacher_id, teacher_no, teacher_name, gender, phone, title, department(学院))
"""
    
    def get_first_intent_prompt(self, history_messages=""):
        """获取第一层意图分析提示词"""
        return self._first_intent_prompt.format(history_messages=history_messages).strip()
    
    def get_sql_intent_prompt(self, user_role_cn, user_name):
        """获取数据库查询确认提示词"""
        return self._sql_intent_prompt.format(
            user_role_cn=user_role_cn,
            user_name=user_name
        ).strip()
    
    def get_chat_system_prompt(self):
        """获取聊天系统提示词"""
        return self._chat_system_prompt.strip()
    
    def get_title_generation_prompt(self, user_input):
        """获取标题生成提示词"""
        return self._title_generation_prompt.format(
            user_input=user_input
        ).strip()
    
    def get_smart_query_prompt(self, user_input, table_structure, permission_condition, history_messages=""):
        """获取智能查询提示词"""
        return self._smart_query_prompt.format(
            history_messages=history_messages,
            user_input=user_input,
            table_structure=table_structure,
            permission_condition=permission_condition
        ).strip()
    
    def get_student_tables(self):
        """获取学生可用的表结构"""
        return self._student_tables.strip()
    
    def get_teacher_tables(self):
        """获取教师可用的表结构"""
        return self._teacher_tables.strip()
    
    def get_permission_check_prompt(self, user_input, user_role_cn, user_name, history_messages=""):
        """获取权限确认提示词"""
        return self._permission_check_prompt.format(
            history_messages=history_messages,
            user_input=user_input,
            user_role_cn=user_role_cn,
            user_name=user_name
        ).strip()
    
    def get_database_summary_prompt(self, user_input, table_data):
        """获取数据库查询结果总结提示词"""
        return f"""
你是一个教育系统智能助手。用户的问题是：{user_input}

以下是查询到的部分表格数据：
{table_data}

请用自然语言简洁地总结以上数据，不要超过200字。直接给出总结即可，不需要任何前缀。
""".strip()
    
    def get_policy_summary_prompt(self, user_input, policy_content):
        """获取政策查询结果总结提示词"""
        return f"""
你是一个教育系统智能助手。用户的问题是：{user_input}

以下是从学生手册中检索到的部分相关内容：
{policy_content}

请用自然语言简单总结以上内容，不超过1000字。可使用markdown格式。
""".strip()
    
    def get_complex_query_split_prompt(self, user_input, history_messages=None):
        """获取复杂查询问题拆分提示词"""
        history_str = ""
        if history_messages and len(history_messages) > 0:
            history_str = "\n".join([msg.get('content', '') for msg in history_messages])
        
        return f"""
你是一个教育系统智能助手的问题拆分专家。

历史对话：
{history_str}

当前输入：
{user_input}

请结合历史对话和当前输入，将用户的问题拆分为简单的两部分，尽可能查询更少信息：
1. 需要从数据库查询的内容（有常见的字段如分数，绩点，学院，班级，教师等）
2. 需要从学生手册查询的内容（有学校的各种政策规定）

请以以下格式输出（不要添加其他内容）：
数据库查询词: [具体查询内容]
学生手册查询词: [具体查询内容]
""".strip()
    
    def get_complex_query_prompt(self, user_input, db_result, policy_content):
        """获取复杂查询综合回答提示词"""
        return f"""
你是一个教育系统智能助手。用户的问题是：{user_input}

以下是从数据库中查询到的数据：
{db_result}

以下是从学生手册中查询到的相关政策内容：
{policy_content}

请结合以上两部分内容，用自然语言完整回答用户的问题。可使用markdown格式，字数控制在1000字以内。
""".strip()
    
    def get_policy_query_intent_prompt(self, user_input, history_messages=None):
        """获取政策查询意图分析提示词"""
        history_str = ""
        if history_messages and len(history_messages) > 0:
            history_str = "\n".join([msg.get('content', '') for msg in history_messages])
        
        return f"""
你是一个教育系统智能助手，需要分析用户想从学生手册中查询什么内容。

历史对话：
{history_str}

当前输入：
{user_input}

请分析用户真正想要查询的主题是什么（部分情况可能要根据历史对话判断）。
请直接输出查询的主题，不要添加其他内容，也不要解释。
""".strip()
