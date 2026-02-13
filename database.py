import sqlite3
import json
from datetime import datetime

def init_db():
    """
    初始化数据库，创建必要的表结构
    """
    conn = sqlite3.connect('cybertcm.db')
    c = conn.cursor()
    
    # 创建用户表
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nickname TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建问卷表
    c.execute('''
    CREATE TABLE IF NOT EXISTS questionnaires (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type_code TEXT NOT NULL,
        type_name TEXT NOT NULL,
        radar_data TEXT NOT NULL,
        energy_data TEXT NOT NULL,
        answers TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # 创建管理员密码表
    c.execute('''
    CREATE TABLE IF NOT EXISTS admin_password (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        password TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    
    # 初始化默认密码
    init_admin_password()

def init_admin_password():
    """
    初始化管理员密码，如果不存在则设置默认密码8888
    """
    conn = sqlite3.connect('cybertcm.db')
    c = conn.cursor()
    
    # 检查是否已存在密码
    c.execute('SELECT COUNT(*) FROM admin_password')
    count = c.fetchone()[0]
    
    if count == 0:
        # 设置默认密码8888
        c.execute('INSERT INTO admin_password (password) VALUES (?)', ('8888',))
        conn.commit()
    
    conn.close()

def verify_admin_password(password):
    """
    验证管理员密码
    
    Args:
        password: 输入的密码
    
    Returns:
        bool: 密码是否正确
    """
    conn = sqlite3.connect('cybertcm.db')
    c = conn.cursor()
    
    c.execute('SELECT password FROM admin_password WHERE id = 1')
    result = c.fetchone()
    
    conn.close()
    
    if result:
        return result[0] == password
    return False

def update_admin_password(current_password, new_password):
    """
    修改管理员密码
    
    Args:
        current_password: 当前密码
        new_password: 新密码
    
    Returns:
        tuple: (是否成功, 错误信息)
    """
    # 先验证当前密码
    if not verify_admin_password(current_password):
        return False, "当前密码错误"
    
    conn = sqlite3.connect('cybertcm.db')
    c = conn.cursor()
    
    try:
        c.execute('''
        UPDATE admin_password 
        SET password = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = 1
        ''', (new_password,))
        conn.commit()
        conn.close()
        return True, "密码修改成功"
    except Exception as e:
        conn.close()
        return False, f"修改失败: {str(e)}"

def get_or_create_user(nickname):
    """
    获取用户，如果不存在则创建
    
    Args:
        nickname: 用户昵称
    
    Returns:
        user_id: 用户ID
    """
    conn = sqlite3.connect('cybertcm.db')
    c = conn.cursor()
    
    # 查找用户
    c.execute('SELECT id FROM users WHERE nickname = ?', (nickname,))
    user = c.fetchone()
    
    if user:
        user_id = user[0]
    else:
        # 创建新用户
        c.execute('INSERT INTO users (nickname) VALUES (?)', (nickname,))
        user_id = c.lastrowid
        conn.commit()
    
    conn.close()
    return user_id

def save_questionnaire(user_id, type_code, type_name, radar_data, energy_data, answers):
    """
    保存问卷数据
    
    Args:
        user_id: 用户ID
        type_code: 体质类型代码
        type_name: 体质类型名称
        radar_data: 雷达图数据
        energy_data: 能量条数据
        answers: 用户答案
    """
    conn = sqlite3.connect('cybertcm.db')
    c = conn.cursor()
    
    # 存储数据
    c.execute('''
    INSERT INTO questionnaires (user_id, type_code, type_name, radar_data, energy_data, answers)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        type_code,
        type_name,
        json.dumps(radar_data),
        json.dumps(energy_data),
        json.dumps(answers)
    ))
    
    conn.commit()
    conn.close()

def save_complete_questionnaire(user_id, part1_result, part2_result, part1_answers, part2_answers, raw_answers):
    """
    保存完整的问卷数据（包含八纲辨证和卫健委两部分）
    
    Args:
        user_id: 用户ID
        part1_result: 八纲辨证结果
        part2_result: 卫健委体质结果
        part1_answers: 八纲辨证答案
        part2_answers: 卫健委答案
        raw_answers: 所有61道题的原始选择
    """
    conn = sqlite3.connect('cybertcm.db')
    c = conn.cursor()
    
    # 创建新的表结构（如果不存在）
    c.execute('''
    CREATE TABLE IF NOT EXISTS complete_questionnaires (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        -- 八纲辨证结果
        bagang_type_code TEXT,
        bagang_type_name TEXT,
        bagang_radar_data TEXT,
        bagang_energy_data TEXT,
        bagang_answers TEXT,
        -- 卫健委结果
        wjw_main_constitution TEXT,
        wjw_main_score INTEGER,
        wjw_main_result TEXT,
        wjw_all_results TEXT,
        wjw_scores TEXT,
        wjw_answers TEXT,
        -- 原始答案
        raw_answers TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # 检查并添加缺失的列
    columns_to_check = ['wjw_scores', 'raw_answers']
    for col in columns_to_check:
        try:
            c.execute(f'SELECT {col} FROM complete_questionnaires LIMIT 1')
        except sqlite3.OperationalError:
            # 列不存在，添加它
            c.execute(f'ALTER TABLE complete_questionnaires ADD COLUMN {col} TEXT')
    
    # 存储完整数据
    c.execute('''
    INSERT INTO complete_questionnaires (
        user_id, 
        bagang_type_code, bagang_type_name, bagang_radar_data, bagang_energy_data, bagang_answers,
        wjw_main_constitution, wjw_main_score, wjw_main_result, wjw_all_results, wjw_scores, wjw_answers,
        raw_answers
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    conn.close()

def get_user_questionnaires(user_id):
    """
    获取用户的问卷历史
    
    Args:
        user_id: 用户ID
    
    Returns:
        问卷历史列表
    """
    conn = sqlite3.connect('cybertcm.db')
    c = conn.cursor()
    
    c.execute('''
    SELECT id, type_code, type_name, created_at 
    FROM questionnaires 
    WHERE user_id = ? 
    ORDER BY created_at DESC
    ''', (user_id,))
    
    questionnaires = []
    for row in c.fetchall():
        questionnaires.append({
            'id': row[0],
            'type_code': row[1],
            'type_name': row[2],
            'created_at': row[3]
        })
    
    conn.close()
    return questionnaires

def get_questionnaire_detail(questionnaire_id):
    """
    获取问卷详细信息
    
    Args:
        questionnaire_id: 问卷ID
    
    Returns:
        问卷详细信息
    """
    conn = sqlite3.connect('cybertcm.db')
    c = conn.cursor()
    
    c.execute('''
    SELECT type_code, type_name, radar_data, energy_data, answers, created_at 
    FROM questionnaires 
    WHERE id = ?
    ''', (questionnaire_id,))
    
    row = c.fetchone()
    if row:
        return {
            'type_code': row[0],
            'type_name': row[1],
            'radar_data': json.loads(row[2]),
            'energy_data': json.loads(row[3]),
            'answers': json.loads(row[4]),
            'created_at': row[5]
        }
    
    conn.close()
    return None

# ==================== 数据管理功能 ====================

def get_all_users():
    """
    获取所有用户列表
    
    Returns:
        用户列表，包含用户ID、昵称、创建时间和问卷数量
    """
    conn = sqlite3.connect('cybertcm.db')
    c = conn.cursor()
    
    c.execute('''
    SELECT u.id, u.nickname, u.created_at, COUNT(q.id) as questionnaire_count
    FROM users u
    LEFT JOIN questionnaires q ON u.id = q.user_id
    GROUP BY u.id
    ORDER BY u.created_at DESC
    ''')
    
    users = []
    for row in c.fetchall():
        users.append({
            'id': row[0],
            'nickname': row[1],
            'created_at': row[2],
            'questionnaire_count': row[3]
        })
    
    conn.close()
    return users

def get_all_questionnaires(limit=None, offset=0):
    """
    获取所有问卷数据
    
    Args:
        limit: 限制返回数量
        offset: 偏移量
    
    Returns:
        问卷列表
    """
    conn = sqlite3.connect('cybertcm.db')
    c = conn.cursor()
    
    query = '''
    SELECT q.id, u.nickname, q.type_code, q.type_name, q.created_at
    FROM questionnaires q
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
    
    conn.close()
    return questionnaires

def get_statistics():
    """
    获取数据统计信息
    
    Returns:
        统计信息字典
    """
    conn = sqlite3.connect('cybertcm.db')
    c = conn.cursor()
    
    # 总用户数
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    
    # 总问卷数
    c.execute('SELECT COUNT(*) FROM questionnaires')
    total_questionnaires = c.fetchone()[0]
    
    # 体质类型分布
    c.execute('''
    SELECT type_code, type_name, COUNT(*) as count
    FROM questionnaires
    GROUP BY type_code
    ORDER BY count DESC
    ''')
    
    type_distribution = []
    for row in c.fetchall():
        type_distribution.append({
            'type_code': row[0],
            'type_name': row[1],
            'count': row[2]
        })
    
    # 今日新增
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('''
    SELECT COUNT(*) FROM questionnaires
    WHERE DATE(created_at) = ?
    ''', (today,))
    today_count = c.fetchone()[0]
    
    conn.close()
    
    return {
        'total_users': total_users,
        'total_questionnaires': total_questionnaires,
        'today_count': today_count,
        'type_distribution': type_distribution
    }

def export_to_csv(filename='cybertcm_export.csv'):
    """
    导出所有数据到CSV文件
    
    Args:
        filename: 导出文件名
    
    Returns:
        导出的文件路径
    """
    import csv
    
    conn = sqlite3.connect('cybertcm.db')
    c = conn.cursor()
    
    # 查询所有问卷数据
    c.execute('''
    SELECT q.id, u.nickname, q.type_code, q.type_name, q.radar_data, q.created_at
    FROM questionnaires q
    JOIN users u ON q.user_id = u.id
    ORDER BY q.created_at DESC
    ''')
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        # 写入表头
        writer.writerow(['ID', '用户昵称', '体质代码', '体质名称', '雷达数据', '提交时间'])
        
        # 写入数据
        for row in c.fetchall():
            writer.writerow([
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5]
            ])
    
    conn.close()
    return filename

def export_to_excel(filename='cybertcm_export.xlsx'):
    """
    导出所有数据到Excel文件（包含八纲辨证和卫健委两部分结果）
    
    Args:
        filename: 导出文件名
    
    Returns:
        导出的文件路径
    """
    try:
        import pandas as pd
        import json
        
        conn = sqlite3.connect('cybertcm.db')
        
        # 查询完整问卷数据（包含两部分）
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
            # 如果没有完整问卷数据，尝试查询旧版问卷数据
            df = pd.read_sql_query('''
            SELECT q.id, u.nickname, q.type_code, q.type_name, q.radar_data, q.energy_data, q.created_at
            FROM questionnaires q
            JOIN users u ON q.user_id = u.id
            ORDER BY q.created_at DESC
            ''', conn)
            
            # 重命名列
            df.columns = ['ID', '用户昵称', '体质代码', '体质名称', '雷达数据', '能量数据', '提交时间']
        else:
            # 处理完整问卷数据
            # 解析雷达数据
            def parse_radar(radar_json):
                try:
                    radar = json.loads(radar_json) if radar_json else {}
                    return ', '.join([f"{k}:{v}" for k, v in radar.items()])
                except:
                    return radar_json
            
            # 解析卫健委所有体质结果
            def parse_wjw_results(wjw_json):
                try:
                    results = json.loads(wjw_json) if wjw_json else {}
                    return ', '.join([f"{k}({v['score']}分-{v['result']})" for k, v in results.items()])
                except:
                    return wjw_json
            
            # 解析卫健委9维度原始分数
            def parse_wjw_scores(scores_json):
                try:
                    scores = json.loads(scores_json) if scores_json else {}
                    return scores
                except:
                    return {}
            
            # 解析原始答案（确保中文正常显示，按题号排序）
            def parse_raw_answers(raw_json):
                try:
                    answers = json.loads(raw_json) if raw_json else {}
                    
                    # 分离两组题目
                    q_items = []  # 八纲辨证题目 (q_1 到 q_28)
                    w_items = []  # 卫健委题目 (wjw_q_1 到 wjw_q_33)
                    
                    for key, value in answers.items():
                        if key.startswith('q_'):
                            q_num = int(key.replace('q_', ''))
                            q_items.append((q_num, f"Q{q_num}:{value}"))
                        elif key.startswith('wjw_q_'):
                            q_num = int(key.replace('wjw_q_', ''))
                            w_items.append((q_num, f"W{q_num}:{value}"))
                    
                    # 按数字排序
                    q_items.sort(key=lambda x: x[0])
                    w_items.sort(key=lambda x: x[0])
                    
                    # 合并结果（先Q后W）
                    formatted = [item[1] for item in q_items] + [item[1] for item in w_items]
                    
                    return '; '.join(formatted)
                except:
                    return raw_json
            
            # 应用解析函数
            df['八纲雷达数据'] = df['bagang_radar_data'].apply(parse_radar)
            df['八纲能量数据'] = df['bagang_energy_data'].apply(parse_radar)
            df['卫健委各体质结果'] = df['wjw_all_results'].apply(parse_wjw_results)
            
            # 处理原始答案列
            if 'raw_answers' in df.columns:
                df['原始答案'] = df['raw_answers'].apply(parse_raw_answers)
            
            # 展开卫健委9维度分数
            wjw_scores_df = df['wjw_scores'].apply(parse_wjw_scores).apply(pd.Series)
            
            # 重命名列
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
            
            # 合并数据
            df = pd.concat([df, wjw_scores_df], axis=1)
            
            # 选择要导出的列（包含9维度分数）
            columns = ['ID', '用户昵称', '八纲体质代码', '八纲体质名称', '八纲雷达数据', '八纲能量数据',
                       '卫健委主要体质', '卫健委主要体质得分', '卫健委主要体质判定']
            
            # 添加9维度分数列（如果存在）
            constitution_types = ['气虚质', '阳虚质', '阴虚质', '痰湿质', '湿热质', '血瘀质', '气郁质', '特禀质', '平和质']
            for ctype in constitution_types:
                if ctype in df.columns:
                    columns.append(ctype)
            
            columns.extend(['卫健委各体质结果', '原始答案', '提交时间'])
            
            # 只选择存在的列
            existing_columns = [c for c in columns if c in df.columns]
            df = df[existing_columns]
        
        # 保存到Excel
        df.to_excel(filename, index=False, engine='openpyxl')
        
        conn.close()
        return filename
    except ImportError:
        print("请先安装pandas和openpyxl: pip install pandas openpyxl")
        return None

def search_questionnaires(nickname=None, type_code=None, start_date=None, end_date=None):
    """
    搜索问卷数据
    
    Args:
        nickname: 用户昵称（模糊搜索）
        type_code: 体质类型代码
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
    
    Returns:
        符合条件的问卷列表
    """
    conn = sqlite3.connect('cybertcm.db')
    c = conn.cursor()
    
    query = '''
    SELECT q.id, u.nickname, q.type_code, q.type_name, q.created_at
    FROM questionnaires q
    JOIN users u ON q.user_id = u.id
    WHERE 1=1
    '''
    params = []
    
    if nickname:
        query += ' AND u.nickname LIKE ?'
        params.append(f'%{nickname}%')
    
    if type_code:
        query += ' AND q.type_code = ?'
        params.append(type_code)
    
    if start_date:
        query += ' AND DATE(q.created_at) >= ?'
        params.append(start_date)
    
    if end_date:
        query += ' AND DATE(q.created_at) <= ?'
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
    
    conn.close()
    return questionnaires

def get_database_info():
    """
    获取数据库信息
    
    Returns:
        数据库信息字典
    """
    import os
    
    db_path = 'cybertcm.db'
    
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        file_size_mb = file_size / (1024 * 1024)
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # 获取表信息
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in c.fetchall()]
        
        conn.close()
        
        return {
            'file_path': db_path,
            'file_size': f"{file_size_mb:.2f} MB",
            'tables': tables
        }
    else:
        return None
