
"""
数据库模块
处理数据库连接和用户验证
"""
import pymysql
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_CHARSET

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset=DB_CHARSET
    )

def verify_user(account, password):
    """
    验证用户：先查学生表，再查教师表
    返回：{'role': 'student'|'teacher'|None, 'data': {}}
    """
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 先查学生表
            sql_student = "SELECT student_no as account, student_name as name, 'student' as role FROM students WHERE student_no = %s AND edu_sys_password = %s"
            cursor.execute(sql_student, (account, password))
            student = cursor.fetchone()
            if student:
                return student
            
            # 再查教师表
            sql_teacher = "SELECT teacher_no as account, teacher_name as name, 'teacher' as role FROM teachers WHERE teacher_no = %s AND edu_sys_password = %s"
            cursor.execute(sql_teacher, (account, password))
            teacher = cursor.fetchone()
            if teacher:
                return teacher
            
            return None
    finally:
        conn.close()

# ==================== 对话会话管理 ====================
def create_conversation(account, user_role, title='新对话'):
    """创建新对话"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO conversations (account, user_role, title) VALUES (%s, %s, %s)"
            cursor.execute(sql, (account, user_role, title))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()

def get_conversations(account):
    """获取用户的所有对话"""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM conversations WHERE account = %s ORDER BY updated_at DESC"
            cursor.execute(sql, (account,))
            return cursor.fetchall()
    finally:
        conn.close()

def get_latest_conversation(account):
    """获取用户最近的对话"""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM conversations WHERE account = %s ORDER BY updated_at DESC LIMIT 1"
            cursor.execute(sql, (account,))
            return cursor.fetchone()
    finally:
        conn.close()

def delete_conversation(conversation_id):
    """删除对话"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "DELETE FROM conversations WHERE conversation_id = %s"
            cursor.execute(sql, (conversation_id,))
            conn.commit()
            return True
    finally:
        conn.close()

def update_conversation_title(conversation_id, title):
    """更新对话标题"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE conversations SET title = %s, updated_at = NOW() WHERE conversation_id = %s"
            cursor.execute(sql, (title, conversation_id))
            conn.commit()
            return True
    finally:
        conn.close()

# ==================== 聊天消息管理 ====================
def add_message(conversation_id, role, content):
    """添加消息"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO messages (conversation_id, role, content) VALUES (%s, %s, %s)"
            cursor.execute(sql, (conversation_id, role, content))
            conn.commit()
            
            # 更新对话的 updated_at
            sql_update = "UPDATE conversations SET updated_at = NOW() WHERE conversation_id = %s"
            cursor.execute(sql_update, (conversation_id,))
            conn.commit()
            
            return cursor.lastrowid
    finally:
        conn.close()

def get_messages(conversation_id, limit=60):
    """获取对话的历史消息（默认最近60条）"""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 直接按时间正序排列
            sql = """
                SELECT * FROM messages 
                WHERE conversation_id = %s 
                ORDER BY created_at ASC 
                LIMIT %s
            """
            cursor.execute(sql, (conversation_id, limit))
            return list(cursor.fetchall())
    finally:
        conn.close()

def clear_messages(conversation_id):
    """清空对话的所有消息"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "DELETE FROM messages WHERE conversation_id = %s"
            cursor.execute(sql, (conversation_id,))
            conn.commit()
            
            # 更新对话的 updated_at
            sql_update = "UPDATE conversations SET updated_at = NOW() WHERE conversation_id = %s"
            cursor.execute(sql_update, (conversation_id,))
            conn.commit()
            
            return True
    finally:
        conn.close()

