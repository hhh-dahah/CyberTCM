import pandas as pd
import numpy as np
import math
import io
import os

# --- 1. 数据加载模块 ---

def load_data():
    """
    加载问题库和文案库 (从 Excel 文件)。
    """
    try:
        # 直接读取Excel文件的不同工作表
        df_questions = pd.read_excel("database.xlsx", sheet_name="Questions")
        df_types = pd.read_excel("database.xlsx", sheet_name="Types")
        
        # 数据清洗：将 type_code 设为索引
        if 'type_code' in df_types.columns:
            df_types['type_code'] = df_types['type_code'].astype(str).str.strip()
            df_types.set_index("type_code", inplace=True)
            
        return df_questions, df_types
        
    except FileNotFoundError:
        print("警告：未找到数据库文件，正在加载备用数据...")
        return load_mock_data()
    except Exception as e:
        print(f"数据加载错误: {e}")
        return load_mock_data()

def load_questions():
    """
    仅加载问题库 (用于 app.py 初始化问卷)。
    """
    try:
        return pd.read_excel("database.xlsx", sheet_name="Questions")
    except:
        return load_mock_data()[0]

def load_mock_data():
    """
    备用数据生成器 (修复了长度不一致的 Bug)
    """
    # 1. 模拟问题数据 (28道题)
    questions_list = [
        "1. 你是否比周围的人更容易觉得冷？", "2. 吃凉的东西肚子会不舒服吗？", "3. 阴冷天气关节会痛吗？", # Cold (3)
        "4. 容易面红耳赤或长痘吗？", "5. 经常口干舌燥想喝冰水？", "6. 容易心烦意乱？", # Heat (3)
        "7. 容易疲劳不想说话？", "8. 容易感冒？", "9. 容易出虚汗？", "10. 蹲下起立眼黑？", # Void (4)
        "11. 肚子胀气或便秘？", "12. 声音洪亮中气足？", "13. 食欲旺盛容易积食？", # Solid (3)
        "14. 皮肤嘴唇常年干燥？", "15. 干咳无痰？", "16. 皮肤干痒？", # Dry (3)
        "17. 脸上出油头发油？", "18. 身体沉重睡不醒？", "19. 大便粘马桶？", "20. 嘴里有异味？", # Wet (4)
        "21. 情绪低落爱叹气？", "22. 胸闷肋痛？", "23. 喉咙有异物感？", "24. 乳房或小腹胀痛？", # Qi (4)
        "25. 身上容易有淤青？", "26. 脸色暗沉嘴唇紫？", "27. 皮肤粗糙有甲错？", "28. 健忘？"  # Blood (4)
    ]
    
    q_data = {
        "id": range(1, 29), # 28个ID
        "question": questions_list, # 28个问题
        "dimension": ["cold"]*3 + ["heat"]*3 + ["void"]*4 + ["solid"]*3 + ["dry"]*3 + ["wet"]*4 + ["qi"]*4 + ["blood"]*4,
        "weight": [1] * 28
    }
    
    df_q = pd.DataFrame(q_data)
    
    # 2. 模拟体质数据 (Types Fallback)
    csv_content = """type_code,name,slogan,simple_description,factory_setting,bug_warning,teammate_cp,keep,stop,start
CVDQ,听风者,听不到才听得见,世界太吵你只是关小了音量,低功耗模式屏蔽干扰,容易emo|社交电量低,HSDQ,晒背,熬夜,喝热水
SSR,天选之子,阴阳平和,六边形战士,你的身体是完美的平衡态,太完美遭人嫉妒,None,保持现状,瞎折腾,继续优秀"""
    
    df_t = pd.read_csv(io.StringIO(csv_content))
    if 'type_code' in df_t.columns:
        df_t['type_code'] = df_t['type_code'].astype(str).str.strip()
        df_t.set_index("type_code", inplace=True)
    
    return df_q, df_t

# --- 2. 核心算法模块 ---

def calculate_results(session_state, df_questions, df_types):
    """
    计算逻辑
    """
    # 1. 提取用户答案
    user_answers = {}
    for key, value in session_state.items():
        if key.startswith("q_"):
            user_answers[key] = value

    # 2. 初始化分数
    dimensions = ['cold', 'heat', 'void', 'solid', 'dry', 'wet', 'qi', 'blood']
    raw_scores = {dim: 0 for dim in dimensions}
    
    # 3. 计算原始分
    for index, row in df_questions.iterrows():
        qid = row['id']
        dim = row['dimension']
        ans_str = user_answers.get(f"q_{qid}")
        if ans_str:
            try:
                # 兼容中文括号和英文括号
                score_part = ans_str.replace('（', '(').split('(')[1]
                score = int(score_part.split('分')[0])
                raw_scores[dim] += score
            except:
                pass

    # 4. 归一化 (0-100)
    norm_scores = {}
    for dim, raw in raw_scores.items():
        if dim in ['cold', 'heat', 'solid', 'dry']: 
            n_score = (raw - 3) / 12 * 100
        else: 
            n_score = (raw - 4) / 16 * 100
        norm_scores[dim] = max(0, min(100, n_score))

    # 5. 生成代码
    code_T = 'C' if norm_scores['cold'] >= norm_scores['heat'] else 'H'
    max_T = max(norm_scores['cold'], norm_scores['heat'])
    
    code_E = 'V' if norm_scores['void'] >= norm_scores['solid'] else 'S'
    max_E = max(norm_scores['void'], norm_scores['solid'])
    
    code_H = 'D' if norm_scores['dry'] >= norm_scores['wet'] else 'W'
    max_H = max(norm_scores['dry'], norm_scores['wet'])
    
    code_C = 'Q' if norm_scores['qi'] >= norm_scores['blood'] else 'B'
    max_C = max(norm_scores['qi'], norm_scores['blood'])
    
    final_code = code_T + code_E + code_H + code_C

    # 6. 计算模长 (健康度)
    magnitude = math.sqrt(max_T**2 + max_E**2 + max_H**2 + max_C**2)
    is_ssr = False
    health_level = 2
    
    if magnitude < 35:
        is_ssr = True
        health_level = 1
        final_code = "SSR" 
    elif magnitude >= 90:
        health_level = 3

    # 7. 组装结果
    # 确保 final_code 存在于表中
    if final_code in df_types.index:
        type_data = df_types.loc[final_code]
    else:
        # 兜底策略：如果没找到 (比如 SSR)，用第一个数据代替，但改名
        type_data = df_types.iloc[0].copy()
        if final_code == "SSR":
             type_data["name"] = "天选之子 (平和质)"
             type_data["slogan"] = "阴阳平衡，六边形战士"
             type_data["simple_description"] = "你的身体处于完美的动态平衡中。"
        else:
             type_data["name"] = f"未收录 ({final_code})"

    def parse_list(text):
        if pd.isna(text): return []
        text_str = str(text)
        if '|' in text_str:
            return text_str.split('|')
        return text_str.split('/')

    result_json = {
        "user_info": {
            "is_ssr": is_ssr,
            "type_code": final_code,
            "type_name": type_data["name"],
            "rarity": "SSR" if is_ssr else "R",
            "health_level": health_level,
            "magnitude": round(magnitude, 1)
        },
        "social_badge": {
            "slogan": type_data.get("slogan", ""),
            "poem": type_data.get("simple_description", ""),
            "simple_description": type_data.get("simple_description", ""),
            "factory_setting": type_data.get("factory_setting", ""),
            "bug_warning": parse_list(type_data.get("bug_warning", "")),
            "teammate": type_data.get("teammate_cp", "")
        },
        "radar_chart": norm_scores, 
        "energy_bars": [
            {"label": "温度", "left": "❄️ 寒", "right": "🔥 热", "val": norm_scores['heat'] - norm_scores['cold']},
            {"label": "能量", "left": "☁️ 虚", "right": "💎 实", "val": norm_scores['solid'] - norm_scores['void']},
            {"label": "环境", "left": "🌵 燥", "right": "💧 湿", "val": norm_scores['wet'] - norm_scores['dry']},
            {"label": "通畅", "left": "🌀 郁", "right": "🩸 瘀", "val": norm_scores['blood'] - norm_scores['qi']},
        ],
        "action_guide": {
            "keep": parse_list(type_data.get("keep", "")),
            "stop": parse_list(type_data.get("stop", "")),
            "start": parse_list(type_data.get("start", ""))
        }
    }
    
    return result_json