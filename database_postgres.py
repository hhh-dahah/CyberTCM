import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os
from datetime import datetime

# 兼容 Streamlit Cloud 和本地环境的配置读取
def get_db_config():
    """获取数据库配置，支持 Streamlit Secrets 和环境变量"""
    print("[DB DEBUG] 开始加载数据库配置...")
    
    # 优先尝试从 Streamlit Secrets 读取（Streamlit Cloud 环境）
    try:
        import streamlit as st
        print(f"[DB DEBUG] Streamlit secrets 可用：{hasattr(st, 'secrets')}")
        
        if hasattr(st, 'secrets'):
            # 检查所有必需的键
            required_keys = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME']
            available_keys = [k for k in required_keys if k in st.secrets]
            missing_keys = [k for k in required_keys if k not in st.secrets]
            
            print(f"[DB DEBUG] Secrets 中可用的键：{available_keys}")
            if missing_keys:
                print(f"[DB DEBUG] Secrets 中缺少的键：{missing_keys}")
            
            if all(k in st.secrets for k in required_keys):
                config = {
                    'DB_USER': st.secrets['DB_USER'],
                    'DB_PASSWORD': st.secrets['DB_PASSWORD'],
                    'DB_HOST': st.secrets['DB_HOST'],
                    'DB_PORT': st.secrets['DB_PORT'],
                    'DB_NAME': st.secrets['DB_NAME']
                }
                print(f"[DB DEBUG] ✓ 成功从 Streamlit Secrets 加载配置")
                print(f"[DB DEBUG]   HOST: {config['DB_HOST']}")
                print(f"[DB DEBUG]   PORT: {config['DB_PORT']}")
                print(f"[DB DEBUG]   USER: {config['DB_USER']}")
                print(f"[DB DEBUG]   DATABASE: {config['DB_NAME']}")
                print(f"[DB DEBUG]   PASSWORD 长度：{len(str(config['DB_PASSWORD']))}")
                return config
    except Exception as e:
        print(f"[DB DEBUG] ✗ 读取 Secrets 失败：{e}")
        import traceback
        print(f"[DB DEBUG] {traceback.format_exc()}")
    
    # 回退到环境变量（本地开发或其他平台）
    print("[DB DEBUG] 回退到环境变量...")
    from dotenv import load_dotenv
    load_dotenv()
    config = {
        'DB_USER': os.getenv("DB_USER"),
        'DB_PASSWORD': os.getenv("DB_PASSWORD"),
        'DB_HOST': os.getenv("DB_HOST"),
        'DB_PORT': os.getenv("DB_PORT"),
        'DB_NAME': os.getenv("DB_NAME")
    }
    
    print(f"[DB DEBUG] 环境变量配置:")
    for key, value in config.items():
        if key == 'DB_PASSWORD':
            print(f"[DB DEBUG]   {key}: {'已设置' if value else '未设置'}")
        else:
            print(f"[DB DEBUG]   {key}: {value}")
    
    return config

# 数据库配置缓存（延迟加载）
_db_config = None

def _get_cached_config():
    """获取缓存的数据库配置，首次调用时加载"""
    global _db_config
    if _db_config is None:
        print("[DB DEBUG] 首次加载数据库配置...")
        _db_config = get_db_config()
    return _db_config

def get_connection():
    """获取数据库连接"""
    db_config = _get_cached_config()
    
    DB_USER = db_config['DB_USER']
    DB_PASSWORD = db_config['DB_PASSWORD']
    DB_HOST = db_config['DB_HOST']
    DB_PORT = db_config['DB_PORT']
    DB_NAME = db_config['DB_NAME']
    
    print(f"[DB DEBUG] 尝试连接数据库...")
    print(f"[DB DEBUG]   Host: {DB_HOST}:{DB_PORT}")
    print(f"[DB DEBUG]   Database: {DB_NAME}")
    print(f"[DB DEBUG]   User: {DB_USER}")
    
    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        missing = []
        if not DB_USER: missing.append('USER')
        if not DB_PASSWORD: missing.append('PASSWORD')
        if not DB_HOST: missing.append('HOST')
        if not DB_PORT: missing.append('PORT')
        if not DB_NAME: missing.append('NAME')
        raise ValueError(f"数据库配置缺失：{', '.join(missing)}")
    
    try:
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME
        )
        print(f"[DB DEBUG] ✓ 数据库连接成功！")
        return conn
    except psycopg2.OperationalError as e:
        print(f"[DB DEBUG] ✗ 数据库连接失败！")
        print(f"[DB DEBUG]   错误类型：psycopg2.OperationalError")
        print(f"[DB DEBUG]   错误详情：{e}")
        print(f"[DB DEBUG] 连接参数:")
        print(f"[DB DEBUG]   Host: {DB_HOST}:{DB_PORT}")
        print(f"[DB DEBUG]   Database: {DB_NAME}")
        print(f"[DB DEBUG]   User: {DB_USER}")
        print(f"[DB DEBUG]   Password: {'*' * len(str(DB_PASSWORD))}")
        raise

def init_db():
    """初始化数据库连接（创建表结构）"""
    print("数据库已就绪")

def init_admin_password():
    """初始化管理员密码"""
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute('SELECT COUNT(*) FROM admin_password')
            count = c.fetchone()[0]
            if count == 0:
                c.execute('INSERT INTO admin_password (password) VALUES (%s)', ('8888',))
                conn.commit()

def verify_admin_password(password):
    """验证管理员密码"""
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute('SELECT password FROM admin_password WHERE id = 1')
            result = c.fetchone()
            if result:
                return result[0] == password
            return False

def update_admin_password(current_password, new_password):
    """修改管理员密码"""
    if not verify_admin_password(current_password):
        return False, "当前密码错误"
    try:
        with get_connection() as conn:
            with conn.cursor() as c:
                c.execute('UPDATE admin_password SET password = %s, updated_at = NOW() WHERE id = 1', (new_password,))
                conn.commit()
                return True, "密码修改成功"
    except Exception as e:
        return False, f"修改失败: {str(e)}"

def get_or_create_user(nickname):
    """获取用户，如果不存在则创建"""
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute('SELECT id FROM users WHERE nickname = %s', (nickname,))
            user = c.fetchone()
            if user:
                return user[0]
            else:
                c.execute('INSERT INTO users (nickname) VALUES (%s) RETURNING id', (nickname,))
                user_id = c.fetchone()[0]
                conn.commit()
                return user_id

def save_complete_questionnaire(user_id, part1_result, part2_result, part1_answers, part2_answers, raw_answers):
    """保存完整的问卷数据"""
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute('''
                INSERT INTO complete_questionnaires (
                    user_id, 
                    bagang_type_code, bagang_type_name, bagang_radar_data, bagang_energy_data, bagang_answers,
                    wjw_main_constitution, wjw_main_score, wjw_main_result, wjw_all_results, wjw_scores, wjw_answers,
                    raw_answers
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                user_id,
                part1_result['user_info']['type_code'],
                part1_result['user_info']['type_name'],
                json.dumps(part1_result['radar_chart']),
                json.dumps(part1_result['energy_bars']),
                json.dumps(part1_answers),
                part2_result['main_constitution'],
                part2_result['main_score'],
                part2_result['main_result'],
                json.dumps(part2_result['constitution_results']),
                json.dumps(part2_result['constitution_scores']),
                json.dumps(part2_answers),
                json.dumps(raw_answers)
            ))
            conn.commit()

def get_statistics():
    """获取数据统计信息"""
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute('SELECT COUNT(*) FROM users')
            total_users = c.fetchone()[0]
            
            c.execute('SELECT COUNT(*) FROM complete_questionnaires')
            total_questionnaires = c.fetchone()[0]
            
            c.execute('''
                SELECT bagang_type_code, bagang_type_name, COUNT(*) as count
                FROM complete_questionnaires
                GROUP BY bagang_type_code, bagang_type_name
                ORDER BY count DESC
            ''')
            
            type_distribution = []
            for row in c.fetchall():
                type_distribution.append({
                    'type_code': row[0],
                    'type_name': row[1],
                    'count': row[2]
                })
            
            today = datetime.now().strftime('%Y-%m-%d')
            c.execute('''
                SELECT COUNT(*) FROM complete_questionnaires
                WHERE DATE(created_at) = %s
            ''', (today,))
            today_count = c.fetchone()[0]
            
            return {
                'total_users': total_users,
                'total_questionnaires': total_questionnaires,
                'today_count': today_count,
                'type_distribution': type_distribution
            }

def search_questionnaires(nickname=None, type_code=None, start_date=None, end_date=None):
    """搜索问卷数据"""
    with get_connection() as conn:
        with conn.cursor() as c:
            query = '''
                SELECT q.id, u.nickname, q.bagang_type_code, q.bagang_type_name, q.created_at
                FROM complete_questionnaires q
                JOIN users u ON q.user_id = u.id
                WHERE 1=1
            '''
            params = []
            
            if nickname:
                query += ' AND u.nickname LIKE %s'
                params.append(f'%{nickname}%')
            
            if type_code:
                query += ' AND q.bagang_type_code = %s'
                params.append(type_code)
            
            if start_date:
                query += ' AND DATE(q.created_at) >= %s'
                params.append(start_date)
            
            if end_date:
                query += ' AND DATE(q.created_at) <= %s'
                params.append(end_date)
            
            query += ' ORDER BY q.created_at DESC'
            
            c.execute(query, params)
            
            questionnaires = []
            for row in c.fetchall():
                questionnaires.append({
                    'id': row[0],
                    'nickname': row[1],
                    'type_code': row[2],
                    'type_name': row[3],
                    'created_at': row[4]
                })
            
            return questionnaires

def export_to_excel(filename='cybertcm_export.xlsx'):
    """导出数据到Excel"""
    try:
        import pandas as pd
        
        with get_connection() as conn:
            df = pd.read_sql_query('''
                SELECT 
                    c.id, u.nickname, 
                    c.bagang_type_code, c.bagang_type_name, c.bagang_radar_data, c.bagang_energy_data,
                    c.wjw_main_constitution, c.wjw_main_score, c.wjw_main_result, c.wjw_all_results, c.wjw_scores,
                    c.raw_answers,
                    c.created_at
                FROM complete_questionnaires c
                JOIN users u ON c.user_id = u.id
                ORDER BY c.created_at DESC
            ''', conn)
            
            if len(df) == 0:
                return None
            
            def parse_radar(radar_json):
                try:
                    radar = json.loads(radar_json) if radar_json else {}
                    return ', '.join([f"{k}:{v}" for k, v in radar.items()])
                except:
                    return radar_json
            
            def parse_wjw_results(wjw_json):
                try:
                    results = json.loads(wjw_json) if wjw_json else {}
                    return ', '.join([f"{k}({v['score']}分-{v['result']})" for k, v in results.items()])
                except:
                    return wjw_json
            
            df['八纲雷达数据'] = df['bagang_radar_data'].apply(parse_radar)
            df['八纲能量数据'] = df['bagang_energy_data'].apply(parse_radar)
            df['卫健委各体质结果'] = df['wjw_all_results'].apply(parse_wjw_results)
            
            df = df.rename(columns={
                'id': 'ID',
                'nickname': '用户昵称',
                'bagang_type_code': '八纲体质代码',
                'bagang_type_name': '八纲体质名称',
                'wjw_main_constitution': '卫健委主要体质',
                'wjw_main_score': '卫健委主要体质得分',
                'wjw_main_result': '卫健委主要体质判定',
                'created_at': '提交时间'
            })
            
            columns = ['ID', '用户昵称', '八纲体质代码', '八纲体质名称', '八纲雷达数据', '八纲能量数据',
                       '卫健委主要体质', '卫健委主要体质得分', '卫健委主要体质判定', '卫健委各体质结果', '提交时间']
            
            existing_columns = [c for c in columns if c in df.columns]
            df = df[existing_columns]
            
            df.to_excel(filename, index=False, engine='openpyxl')
            return filename
    except ImportError:
        print("请先安装pandas和openpyxl: pip install pandas openpyxl")
        return None

def get_all_questionnaires(limit=None, offset=0):
    """获取所有问卷数据"""
    with get_connection() as conn:
        with conn.cursor() as c:
            query = '''
                SELECT q.id, u.nickname, q.bagang_type_code, q.bagang_type_name, q.created_at
                FROM complete_questionnaires q
                JOIN users u ON q.user_id = u.id
                ORDER BY q.created_at DESC
            '''
            
            if limit:
                query += f' LIMIT {limit} OFFSET {offset}'
            
            c.execute(query)
            
            questionnaires = []
            for row in c.fetchall():
                questionnaires.append({
                    'id': row[0],
                    'nickname': row[1],
                    'type_code': row[2],
                    'type_name': row[3],
                    'created_at': row[4]
                })
            
            return questionnaires
