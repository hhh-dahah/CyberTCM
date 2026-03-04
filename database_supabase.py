import json
import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = None

def init_supabase():
    global supabase
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("请在 .env 文件中配置 SUPABASE_URL 和 SUPABASE_KEY")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db():
    init_supabase()
    init_admin_password()

def init_admin_password():
    try:
        response = supabase.table('admin_password').select('*').execute()
        if len(response.data) == 0:
            supabase.table('admin_password').insert({'password': '8888'}).execute()
    except Exception as e:
        print(f"初始化管理员密码失败: {e}")

def verify_admin_password(password):
    try:
        response = supabase.table('admin_password').select('password').eq('id', 1).execute()
        if response.data:
            return response.data[0]['password'] == password
        return False
    except Exception as e:
        print(f"验证密码失败: {e}")
        return False

def update_admin_password(current_password, new_password):
    if not verify_admin_password(current_password):
        return False, "当前密码错误"
    try:
        supabase.table('admin_password').update({
            'password': new_password,
            'updated_at': datetime.now().isoformat()
        }).eq('id', 1).execute()
        return True, "密码修改成功"
    except Exception as e:
        return False, f"修改失败: {str(e)}"

def get_or_create_user(nickname):
    try:
        response = supabase.table('users').select('id').eq('nickname', nickname).execute()
        if response.data:
            return response.data[0]['id']
        else:
            response = supabase.table('users').insert({'nickname': nickname}).execute()
            return response.data[0]['id']
    except Exception as e:
        print(f"获取/创建用户失败: {e}")
        raise

def save_complete_questionnaire(user_id, part1_result, part2_result, part1_answers, part2_answers, raw_answers):
    try:
        data = {
            'user_id': user_id,
            'bagang_type_code': part1_result['user_info']['type_code'],
            'bagang_type_name': part1_result['user_info']['type_name'],
            'bagang_radar_data': json.dumps(part1_result['radar_chart']),
            'bagang_energy_data': json.dumps(part1_result['energy_bars']),
            'bagang_answers': json.dumps(part1_answers),
            'wjw_main_constitution': part2_result['main_constitution'],
            'wjw_main_score': part2_result['main_score'],
            'wjw_main_result': part2_result['main_result'],
            'wjw_all_results': json.dumps(part2_result['constitution_results']),
            'wjw_scores': json.dumps(part2_result['constitution_scores']),
            'wjw_answers': json.dumps(part2_answers),
            'raw_answers': json.dumps(raw_answers)
        }
        supabase.table('complete_questionnaires').insert(data).execute()
    except Exception as e:
        print(f"保存问卷失败: {e}")
        raise

def get_statistics():
    try:
        users_response = supabase.table('users').select('*', count='exact').execute()
        total_users = users_response.count if hasattr(users_response, 'count') else len(users_response.data)
        
        q_response = supabase.table('complete_questionnaires').select('*', count='exact').execute()
        total_questionnaires = q_response.count if hasattr(q_response, 'count') else len(q_response.data)
        
        type_distribution = []
        q_detail = supabase.table('complete_questionnaires').select('bagang_type_code', 'bagang_type_name').execute()
        type_counts = {}
        for item in q_detail.data:
            code = item.get('bagang_type_code')
            name = item.get('bagang_type_name')
            if code:
                key = (code, name)
                type_counts[key] = type_counts.get(key, 0) + 1
        for (code, name), count in type_counts.items():
            type_distribution.append({
                'type_code': code,
                'type_name': name,
                'count': count
            })
        type_distribution.sort(key=lambda x: x['count'], reverse=True)
        
        today = datetime.now().strftime('%Y-%m-%d')
        today_q = supabase.table('complete_questionnaires').select('*', count='exact').gte('created_at', f'{today}T00:00:00').execute()
        today_count = today_q.count if hasattr(today_q, 'count') else len([q for q in today_q.data if q['created_at'].startswith(today)])
        
        return {
            'total_users': total_users,
            'total_questionnaires': total_questionnaires,
            'today_count': today_count,
            'type_distribution': type_distribution
        }
    except Exception as e:
        print(f"获取统计失败: {e}")
        return {
            'total_users': 0,
            'total_questionnaires': 0,
            'today_count': 0,
            'type_distribution': []
        }

def search_questionnaires(nickname=None, type_code=None, start_date=None, end_date=None):
    try:
        query = supabase.table('complete_questionnaires').select(
            'complete_questionnaires.id, users!inner(nickname), bagang_type_code, bagang_type_name, created_at'
        ).order('created_at', desc=True)
        
        if nickname:
            query = query.ilike('users.nickname', f'%{nickname}%')
        if type_code:
            query = query.eq('bagang_type_code', type_code)
        if start_date:
            query = query.gte('created_at', f'{start_date}T00:00:00')
        if end_date:
            query = query.lte('created_at', f'{end_date}T23:59:59')
            
        response = query.execute()
        
        questionnaires = []
        for row in response.data:
            questionnaires.append({
                'id': row['id'],
                'nickname': row['users']['nickname'],
                'type_code': row['bagang_type_code'],
                'type_name': row['bagang_type_name'],
                'created_at': row['created_at']
            })
        return questionnaires
    except Exception as e:
        print(f"搜索失败: {e}")
        return []

def export_to_excel(filename='cybertcm_export.xlsx'):
    try:
        import pandas as pd
        import json
        
        response = supabase.table('complete_questionnaires').select(
            'complete_questionnaires.*, users!inner(nickname)'
        ).order('created_at', desc=True).execute()
        
        if not response.data:
            return None
            
        df = pd.DataFrame(response.data)
        df['nickname'] = df['users'].apply(lambda x: x['nickname'])
        
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
                
        def parse_wjw_scores(scores_json):
            try:
                scores = json.loads(scores_json) if scores_json else {}
                return scores
            except:
                return {}
                
        def parse_raw_answers(raw_json):
            try:
                answers = json.loads(raw_json) if raw_json else {}
                q_items = []
                w_items = []
                for key, value in answers.items():
                    if key.startswith('q_'):
                        q_num = int(key.replace('q_', ''))
                        q_items.append((q_num, f"Q{q_num}:{value}"))
                    elif key.startswith('wjw_q_'):
                        q_num = int(key.replace('wjw_q_', ''))
                        w_items.append((q_num, f"W{q_num}:{value}"))
                q_items.sort(key=lambda x: x[0])
                w_items.sort(key=lambda x: x[0])
                formatted = [item[1] for item in q_items] + [item[1] for item in w_items]
                return '; '.join(formatted)
            except:
                return raw_json
        
        df['八纲雷达数据'] = df['bagang_radar_data'].apply(parse_radar)
        df['八纲能量数据'] = df['bagang_energy_data'].apply(parse_radar)
        df['卫健委各体质结果'] = df['wjw_all_results'].apply(parse_wjw_results)
        
        if 'raw_answers' in df.columns:
            df['原始答案'] = df['raw_answers'].apply(parse_raw_answers)
            
        wjw_scores_df = df['wjw_scores'].apply(parse_wjw_scores).apply(pd.Series)
        
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
        
        df = pd.concat([df, wjw_scores_df], axis=1)
        
        columns = ['ID', '用户昵称', '八纲体质代码', '八纲体质名称', '八纲雷达数据', '八纲能量数据',
                   '卫健委主要体质', '卫健委主要体质得分', '卫健委主要体质判定']
                   
        constitution_types = ['气虚质', '阳虚质', '阴虚质', '痰湿质', '湿热质', '血瘀质', '气郁质', '特禀质', '平和质']
        for ctype in constitution_types:
            if ctype in df.columns:
                columns.append(ctype)
                
        columns.extend(['卫健委各体质结果', '原始答案', '提交时间'])
        existing_columns = [c for c in columns if c in df.columns]
        df = df[existing_columns]
        
        df.to_excel(filename, index=False, engine='openpyxl')
        return filename
    except ImportError:
        print("请先安装pandas和openpyxl: pip install pandas openpyxl")
        return None
