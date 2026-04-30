"""
数据库初始化脚本
执行 init.sql 和 insert_data.sql 文件
"""

import pymysql
from dotenv import load_dotenv
import os
import re

# 加载环境变量
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在目录：database
ROOT_DIR = os.path.dirname(BASE_DIR)                   # 根目录（和 .env 同级）
load_dotenv(os.path.join(ROOT_DIR, ".env"))            # 加载根目录的 .env

# 从 .env 读取配置
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# 连接 MySQL
db = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    charset="utf8mb4",
    client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS
)
cursor = db.cursor()

# 检查数据库是否存在
cursor.execute(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{DB_NAME}'")
if cursor.fetchone():
    print(f"数据库 {DB_NAME} 已存在")
    cursor.close()
    db.close()
    exit()

# 执行 SQL 文件
def execute_sql_file(filename):
    file_path = os.path.join(BASE_DIR, filename)
    with open(file_path, "r", encoding="utf-8") as f:
        sql = f.read()

    # 去除注释
    sql = re.sub(r'--.*?$', '', sql, flags=re.MULTILINE)
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)

    cursor.execute(sql)
    db.commit()
    print(f"执行成功：{filename}")

# 执行建库 + 插数据
execute_sql_file("init.sql")
execute_sql_file("insert_data.sql")

print("\n 数据库初始化全部完成")
cursor.close()
db.close()