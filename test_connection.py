# 测试数据库连接
import sys
sys.path.insert(0, '.')

try:
    import psycopg2
    print('✅ psycopg2 已安装，版本:', psycopg2.__version__)
except ImportError:
    print('❌ psycopg2 未安装')
    sys.exit(1)

from dotenv import load_dotenv
import os

load_dotenv()

USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DBNAME = os.getenv("DB_NAME")

print(f"DB_USER: {USER}")
print(f"DB_HOST: {HOST}")
print(f"DB_PORT: {PORT}")
print(f"DB_NAME: {DBNAME}")

try:
    connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )
    print("✅ Connection successful!")
    
    cursor = connection.cursor()
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print("Current Time:", result)
    
    # 查询所有表
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = cursor.fetchall()
    print("\n📋 数据库中的表:")
    for table in tables:
        print(f"  - {table[0]}")
    
    cursor.close()
    connection.close()
    print("\nConnection closed.")
    
except Exception as e:
    print(f"\n❌ Failed to connect: {e}")
