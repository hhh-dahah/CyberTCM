import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# 调试信息
print(f"[DB DEBUG] DB_USER: {DB_USER}")
print(f"[DB DEBUG] DB_HOST: {DB_HOST}")
print(f"[DB DEBUG] DB_PORT: {DB_PORT}")
print(f"[DB DEBUG] DB_NAME: {DB_NAME}")
print(f"[DB DEBUG] DB_PASSWORD is set: {DB_PASSWORD is not None and len(DB_PASSWORD) > 0}")

def get_connection():
    """获取数据库连接"""
    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        raise ValueError(f"数据库配置缺失: USER={DB_USER}, HOST={DB_HOST}, PORT={DB_PORT}, NAME={DB_NAME}, PASSWORD={'已设置' if DB_PASSWORD else '未设置'}")
    return psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME
    )

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
