import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_KEY: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "SUPABASE_KEY: None")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # 测试连接
    response = supabase.table('users').select('*').limit(1).execute()
    print(f"✅ 连接成功！users 表查询结果: {response.data}")
    
    # 测试插入数据
    test_response = supabase.table('users').insert({'nickname': '测试用户'}).execute()
    print(f"✅ 插入成功！新用户ID: {test_response.data[0]['id']}")
    
    # 测试查询 complete_questionnaires
    q_response = supabase.table('complete_questionnaires').select('*').limit(1).execute()
    print(f"✅ complete_questionnaires 表查询成功！记录数: {len(q_response.data)}")
    
except Exception as e:
    print(f"❌ 错误: {e}")
