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

def save_complete_questionnaire(user_id, part1_result, part2_result, part1_answers, part2_answers):
    """
    保存完整的问卷数据（包含八纲辨证和卫健委两部分）
    
    Args:
        user_id: 用户ID
        part1_result: 八纲辨证结果
        part2_result: 卫健委体质结果
        part1_answers: 八纲辨证答案
        part2_answers: 卫健委答案
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
        wjw_answers TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # 存储完整数据
    c.execute('''
    INSERT INTO complete_questionnaires (
        user_id, 
        bagang_type_code, bagang_type_name, bagang_radar_data, bagang_energy_data, bagang_answers,
        wjw_main_constitution, wjw_main_score, wjw_main_result, wjw_all_results, wjw_answers
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        json.dumps(part2_answers)
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
    导出所有数据到Excel文件
    
    Args:
        filename: 导出文件名
    
    Returns:
        导出的文件路径
    """
    try:
        import pandas as pd
        
        conn = sqlite3.connect('cybertcm.db')
        
        # 查询所有问卷数据
        df = pd.read_sql_query('''
        SELECT q.id, u.nickname, q.type_code, q.type_name, q.radar_data, q.energy_data, q.created_at
        FROM questionnaires q
        JOIN users u ON q.user_id = u.id
        ORDER BY q.created_at DESC
        ''', conn)
        
        # 重命名列
        df.columns = ['ID', '用户昵称', '体质代码', '体质名称', '雷达数据', '能量数据', '提交时间']
        
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
