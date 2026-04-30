
"""
智能数据库查询系统
让AI直接生成SQL语句，支持联表查询
"""
import re
import pymysql
import os
import dotenv

from ...prompts import PromptManager, ContextBuilder

dotenv.load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


class SmartDatabaseQuery:
    """智能数据库查询类"""
    
    # 字段名中文映射
    COLUMN_MAP = {
        'student_no': '学号',
        'student_name': '姓名',
        'gender': '性别',
        'phone': '联系电话',
        'email': '邮箱',
        'major_code': '专业代码',
        'major_name': '专业名称',
        'department': '所属院系',
        'class_name': '班级名称',
        'grade': '年级',
        'course_code': '课程代码',
        'course_name': '课程名称',
        'credits': '学分',
        'hours': '学时',
        'course_type': '课程类型',
        'semester': '学期',
        'classroom': '教室',
        'schedule': '上课时间',
        'usual_score': '平时成绩',
        'final_score': '期末成绩',
        'total_score': '总成绩',
        'grade_point': '绩点',
        'teacher_no': '工号',
        'teacher_name': '教师姓名',
        'title': '职称',
        'student_count': '学生人数',
        'degree_type': '学位类型',
        'duration': '学制'
    }
    
    # 值的中文映射
    VALUE_MAP = {}
    
    def __init__(self, user_role='visitor', account='', user_name=''):
        self.db_config = {
            "host": DB_HOST,
            "port": DB_PORT,
            "user": DB_USER,
            "password": DB_PASSWORD,
            "database": DB_NAME,
            "charset": "utf8mb4"
        }
        self.user_role = user_role
        self.account = account
        self.user_name = user_name
        self.prompt_manager = PromptManager()
        self.context_builder = ContextBuilder(max_history_pairs=3)
    
    def _get_connection(self):
        return pymysql.connect(**self.db_config)
    
    def _get_table_structure(self):
        """获取当前用户可用的表结构"""
        if self.user_role == 'teacher':
            return self.prompt_manager.get_teacher_tables()
        return self.prompt_manager.get_student_tables()
    
    def _get_student_id(self):
        """根据学号获取 student_id"""
        if self.user_role != 'student':
            return None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT student_id FROM students WHERE student_no = %s", (self.account,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except:
            return None
    
    def _get_teacher_id(self):
        """根据工号获取 teacher_id"""
        if self.user_role != 'teacher':
            return None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT teacher_id FROM teachers WHERE teacher_no = %s", (self.account,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except:
            return None
    
    def _get_permission_condition(self):
        """获取权限限制条件"""
        if self.user_role == 'student':
            student_id = self._get_student_id()
            if student_id:
                return f"使用本次查询的用户是学生，student_id：{student_id}，只能查询自己的信息"
            return f"使用本次查询的用户是学生，只能查询自己的信息"
        elif self.user_role == 'teacher':
            teacher_id = self._get_teacher_id()
            if teacher_id:
                return f"使用本次查询的用户是教师，teacher_id：{teacher_id}"
            return f"使用本次查询的用户是教师，可查询所有学生信息和自己信息"
        return ""
    
    def _sanitize_sql(self, sql):
        """SQL安全检查和清理"""
        # 只允许SELECT语句
        if not sql.strip().upper().startswith('SELECT'):
            return None
        
        # 禁止危险操作
        forbidden = ['DELETE', 'DROP', 'INSERT', 'UPDATE', 'ALTER', 'TRUNCATE', 'CREATE', 'EXECUTE']
        for word in forbidden:
            if word.upper() in sql.upper():
                return None

        # 确保学生只能查询自己的数据
        if self.user_role == 'student':
            student_id = self._get_student_id()
            has_permission = False
            # 检查student_id或student_no
            if student_id and str(student_id) in sql:
                has_permission = True
            if f"'{self.account}'" in sql or f'"{self.account}"' in sql:
                has_permission = True
            if not has_permission:
                return None
        
        return sql
    
    def _clean_sql(self, sql):
        """清理SQL，移除注释和占位符"""
        # 移除SQL注释
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'#.*$', '', sql, flags=re.MULTILINE)
        
        # 移除占位符文本，比如 [xxx] 或 【xxx】
        sql = re.sub(r'\[.*?\]', '', sql)
        sql = re.sub(r'【.*?】', '', sql)
        
        # 移除多余的空格和换行
        sql = re.sub(r'\s+', ' ', sql).strip()
        
        return sql
    
    def _extract_sql(self, text):
        """从AI回复中提取SQL语句"""
        # 尝试提取 ```sql ... ``` 格式
        match = re.search(r'```sql\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return self._clean_sql(match.group(1))
        
        # 尝试提取 ``` ... ``` 格式
        match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return self._clean_sql(match.group(1))
        
        # 直接返回文本（假设整个文本就是SQL）
        return self._clean_sql(text)
    
    def _execute_query(self, sql):
        """执行SQL查询"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            conn.close()
            return columns, results
        except Exception as e:
            return None, str(e)
    
    def _format_result(self, columns, results):
        """格式化查询结果为Markdown表格"""
        if not results:
            return "未查询到相关数据"
        
        # 生成Markdown表格
        md = "|"
        for col in columns:
            col_name = self.COLUMN_MAP.get(col, col)
            md += f" {col_name} |"
        md += "\n"
        
        md += "|"
        for _ in columns:
            md += " --- |"
        md += "\n"
        
        for row in results:
            md += "|"
            for col, value in zip(columns, row):
                if hasattr(value, 'normalize'):
                    value = float(value)
                if col in self.VALUE_MAP and value in self.VALUE_MAP[col]:
                    value = self.VALUE_MAP[col][value]
                md += f" {value} |"
            md += "\n"
        
        return md
    
    def query(self, user_input, chat_ai, history_messages=None):
        """
        智能查询主函数
        """
        if self.user_role == 'visitor':
            return "请先登录后再查询信息"
        
        # 构建仅用户的历史消息
        history_str = ""
        if history_messages:
            user_context = self.context_builder.build_user_only_context(history_messages)
            history_str = "\n".join([msg['content'] for msg in user_context])
        
        # 角色名称映射
        role_mapping = {
            'visitor': '访客',
            'student': '学生',
            'teacher': '教师'
        }
        
        # 第一步：权限检查
        if self.user_role != 'teacher':
            permission_prompt = self.prompt_manager.get_permission_check_prompt(
                user_input=user_input,
                user_role_cn=role_mapping.get(self.user_role, self.user_role),
                user_name=self.account if self.user_role == 'student' else self.user_name,
                history_messages=history_str
            )
            # 保存原来的 system_prompt
            original_system_prompt = chat_ai.system_prompt
            chat_ai.system_prompt = permission_prompt
            permission_result = chat_ai.call_chatAI(question="请判断", history_messages=[], debug=False,
                                                      token_description="数据库查询-权限检查")
            # 恢复原来的 system_prompt
            chat_ai.system_prompt = original_system_prompt
            if "否" in permission_result:
                return "抱歉，您无权查询该信息。"
        
        # 第二步：构建提示词并生成SQL
        table_structure = self._get_table_structure()
        permission_condition = self._get_permission_condition()
        
        prompt = self.prompt_manager.get_smart_query_prompt(
            user_input=user_input,
            table_structure=table_structure,
            permission_condition=permission_condition,
            history_messages=history_str
        )
        
        # 让AI生成SQL
        sql_text = chat_ai.call_chatAI(question=prompt, history_messages=[],
                                          token_description="数据库查询-SQL生成")
        
        # 提取SQL
        sql = self._extract_sql(sql_text)
        
        if not sql:
            return "抱歉，无法生成查询语句，请尝试更明确的描述"
        
        # 安全检查
        sql = self._sanitize_sql(sql)
        
        if not sql:
            return "抱歉，查询语句有安全问题，请修改后重试"
        
        # 执行查询
        columns, results = self._execute_query(sql)
        print("[DEBUG] 查询结果 - columns:", columns)
        print("[DEBUG] 查询结果 - results:", results)
        
        if isinstance(results, str):
            return f"查询出错: {results}"
        
        # 格式化结果
        return self._format_result(columns, results)
    
    def query_with_summary(self, user_input, chat_ai, history_messages=None):
        """
        智能查询主函数，带AI总结
        返回 (summary_generator, table_str)
        """
        if self.user_role == 'visitor':
            return iter(["请先登录后再查询信息"]), None
        
        # 构建仅用户的历史消息
        history_str = ""
        if history_messages:
            user_context = self.context_builder.build_user_only_context(history_messages)
            history_str = "\n".join([msg['content'] for msg in user_context])
        
        # 角色名称映射
        role_mapping = {
            'visitor': '访客',
            'student': '学生',
            'teacher': '教师'
        }
        
        # 第一步：权限检查
        if self.user_role != 'teacher':
            permission_prompt = self.prompt_manager.get_permission_check_prompt(
                user_input=user_input,
                user_role_cn=role_mapping.get(self.user_role, self.user_role),
                user_name=self.account if self.user_role == 'student' else self.user_name,
                history_messages=history_str
            )
            # 保存原来的 system_prompt
            original_system_prompt = chat_ai.system_prompt
            chat_ai.system_prompt = permission_prompt
            permission_result = chat_ai.call_chatAI(question="请判断", history_messages=[], debug=False,
                                                      token_description="数据库查询-权限检查")
            # 恢复原来的 system_prompt
            chat_ai.system_prompt = original_system_prompt
            if "否" in permission_result:
                return iter(["抱歉，您无权查询该信息。"]), None
        
        # 第二步：构建提示词并生成SQL
        table_structure = self._get_table_structure()
        permission_condition = self._get_permission_condition()
        
        prompt = self.prompt_manager.get_smart_query_prompt(
            user_input=user_input,
            table_structure=table_structure,
            permission_condition=permission_condition,
            history_messages=history_str
        )
        
        # 让AI生成SQL
        sql_text = chat_ai.call_chatAI(question=prompt, history_messages=[],
                                          token_description="数据库查询-SQL生成")
        
        # 提取SQL
        sql = self._extract_sql(sql_text)
        
        if not sql:
            return iter(["抱歉，无法生成查询语句，请尝试更明确的描述"]), None
        
        # 安全检查
        sql = self._sanitize_sql(sql)
        
        if not sql:
            return iter(["抱歉，查询语句有安全问题，请修改后重试"]), None
        
        # 执行查询
        columns, results = self._execute_query(sql)
        print("[DEBUG] 查询结果 - columns:", columns)
        print("[DEBUG] 查询结果 - results:", results)
        
        if isinstance(results, str):
            return iter([f"查询出错: {results}"]), None
        
        # 格式化结果为表格
        table_str = self._format_result(columns, results)
        
        # 生成AI总结（流式）
        summary_prompt = self.prompt_manager.get_database_summary_prompt(user_input, table_str)
        # 保存原来的 system_prompt
        original_system_prompt = chat_ai.system_prompt
        chat_ai.system_prompt = ""
        summary_generator = chat_ai.call_chatAI_stream(question=summary_prompt, history_messages=[],
                                                          token_description="数据库查询-结果总结")
        # 恢复原来的 system_prompt
        chat_ai.system_prompt = original_system_prompt
        
        return summary_generator, table_str
