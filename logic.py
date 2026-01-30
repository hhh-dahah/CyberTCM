import pandas as pd
import numpy as np
import math

# --- 1. 数据加载模块 ---
def load_questions():
    """读取题库和文案库"""
    try:
        df_questions = pd.read_excel("database.xlsx", sheet_name="Questions")
        df_types = pd.read_excel("database.xlsx", sheet_name="Types")
        # 将 type_code 设为索引，方便查找
        df_types.set_index("type_code", inplace=True)
        return df_questions, df_types
    except Exception as e:
        return None, None

# --- 2. 核心算法模块 ---
def calculate_results(user_answers, df_questions, df_types):
    """
    输入: 用户答案字典, 题库, 文案库
    输出: 完整的 JSON 结构数据
    """
    # 初始化 8 个标量的原始分
    # 结构: {'cold': 0, 'heat': 0, ...}
    dimensions = ['cold', 'heat', 'void', 'solid', 'dry', 'wet', 'qi', 'blood']
    raw_scores = {dim: 0 for dim in dimensions}
    
    # 2.1 计算原始分
    # 遍历题库，找到用户选的答案并累加
    for index, row in df_questions.iterrows():
        qid = row['id']
        dim = row['dimension']
        
        # 获取用户答案 (假设格式 "A. 经常 (5分)") -> 提取数字
        ans_str = user_answers.get(f"q_{qid}")
        if ans_str:
            # 提取括号里的数字： "A. ... (5分)" -> 5
            try:
                score = int(ans_str.split('(')[1].split('分')[0])
                raw_scores[dim] += score
            except:
                pass # 如果解析失败，默认不加分

    # 2.2 归一化处理 (Normalization) -> 0-100分
    # 3题组: cold, heat, solid, dry
    # 4题组: void, wet, qi, blood
    norm_scores = {}
    for dim, raw in raw_scores.items():
        if dim in ['cold', 'heat', 'solid', 'dry']:
            # 公式: (原始分 - 3) / 12 * 100
            n_score = (raw - 3) / 12 * 100
        else:
            # 公式: (原始分 - 4) / 16 * 100
            n_score = (raw - 4) / 16 * 100
        
        # 限制在 0-100 之间 (防止计算溢出)
        norm_scores[dim] = max(0, min(100, n_score))

    # 2.3 维度判定 (生成 4 字母代码)
    # T轴: Cold vs Heat
    code_T = 'C' if norm_scores['cold'] >= norm_scores['heat'] else 'H'
    max_T = max(norm_scores['cold'], norm_scores['heat'])
    
    # E轴: Void vs Solid
    code_E = 'V' if norm_scores['void'] >= norm_scores['solid'] else 'S'
    max_E = max(norm_scores['void'], norm_scores['solid'])
    
    # H轴: Dry vs Wet
    code_H = 'D' if norm_scores['dry'] >= norm_scores['wet'] else 'W'
    max_H = max(norm_scores['dry'], norm_scores['wet'])
    
    # C轴: Qi vs Blood
    code_C = 'Q' if norm_scores['qi'] >= norm_scores['blood'] else 'B'
    max_C = max(norm_scores['qi'], norm_scores['blood'])
    
    # 组合代码 (如 "CSDB")
    final_code = code_T + code_E + code_H + code_C

    # 2.4 健康层级与模长计算 (Magnitude)
    magnitude = math.sqrt(max_T**2 + max_E**2 + max_H**2 + max_C**2)
    
    # 判定 SSR 平和质
    is_ssr = False
    health_level = 2 # 默认亚健康
    
    if magnitude < 35:
        is_ssr = True
        health_level = 1
        final_code = "SSR" # 特殊处理
    elif magnitude >= 90:
        health_level = 3 # 高危

    # --- 3. 数据组装 (JSON Factory) ---
    
    # 从 Excel 获取文案 (如果没有对应的代码，用默认值防止报错)
    if final_code in df_types.index:
        type_data = df_types.loc[final_code]
    else:
        # Fallback 备用数据
        type_data = {
            "name": "未知体质", "slogan": "系统正在校准...", "simple_description": "数据不足，无法解码",
            "factory_setting": "暂无", "bug_warning": "未知", "teammate_cp": "未知",
            "keep": "休息", "stop": "熬夜", "start": "喝水"
        }

    # 解析竖线分隔的列表
    def parse_list(text):
        if pd.isna(text): return []
        return str(text).split('|')

    result_json = {
        "user_info": {
            "is_ssr": is_ssr,
            "type_code": final_code,
            "type_name": type_data["name"],
            "rarity": "SSR" if is_ssr else "R",
            "health_level": health_level, # 1=绿, 2=黄, 3=红
            "magnitude": round(magnitude, 1)
        },
        "social_badge": {
            "slogan": type_data["slogan"],
            "simple_description": type_data["simple_description"],
            "factory_setting": type_data["factory_setting"],
            "bug_warning": parse_list(type_data["bug_warning"]),
            "teammate": type_data["teammate_cp"]
        },
        "radar_chart": norm_scores, # 直接把 8 个分数值传过去
        "energy_bars": [
            # 计算双向进度条位置: (右 - 左)
            {"label": "温度", "left": "寒", "right": "热", "val": norm_scores['heat'] - norm_scores['cold']},
            {"label": "能量", "left": "虚", "right": "实", "val": norm_scores['solid'] - norm_scores['void']},
            {"label": "环境", "left": "燥", "right": "湿", "val": norm_scores['wet'] - norm_scores['dry']},
            {"label": "通畅", "left": "郁", "right": "瘀", "val": norm_scores['blood'] - norm_scores['qi']},
        ],
        "action_guide": {
            "keep": parse_list(type_data["keep"]),
            "stop": parse_list(type_data["stop"]),
            "start": parse_list(type_data["start"])
        }
    }
    
    return result_json