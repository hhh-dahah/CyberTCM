import pandas as pd
import streamlit as st

# 1. 读取题库的函数
def load_questions():
    try:
        # 读取 Excel 文件
        df = pd.read_excel("database.xlsx", sheet_name="Questions")
        return df
    except Exception as e:
        # 如果找不到文件，为了不报错，我们手动造几条假数据
        st.error(f"⚠️ 题库读取失败: {e}")
        st.warning("正在使用备用测试数据...")
        data = {
            "id": [1, 2, 3, 4],
            "question": [
                "1. 你手脚经常冰凉吗？", 
                "2. 你容易口腔溃疡吗？",
                "3. 你容易感冒吗？",
                "4. 你的皮肤容易出油吗？"
            ],
            "dimension": ["阳虚", "阴虚", "气虚", "湿热"], # 对应的体质维度
            "weight": [1.0, 1.0, 1.0, 1.0]
        }
        return pd.DataFrame(data)

# 2. 核心算分算法 (Brain)
def calculate_score(user_answers, df_questions):
    """
    输入: 用户选的答案 (字典), 题库 (DataFrame)
    输出: 一个包含 9 种体质得分的字典
    """
    # 初始化 9 种体质的得分
    scores = {
        "阳虚": 0, "阴虚": 0, "气虚": 0, "痰湿": 0, 
        "湿热": 0, "血瘀": 0, "特禀": 0, "气郁": 0, "平和": 0
    }
    
    # 遍历每一道题，计算得分
    for index, row in df_questions.iterrows():
        qid = row['id']
        dim = row['dimension'] # 这道题属于哪个体质 (例如 "阳虚")
        
        # 获取用户的选择 (A/B/C/D/E)
        # 注意：这里假设 session_state 里存的是 "A. 经常", "B. 偶尔" 这种
        answer_text = user_answers.get(f"q_{qid}")
        
        if answer_text:
            # 简单的计分逻辑 (你们后面可以改)
            # A=5分(非常符合), B=4, C=3, D=2, E=1(完全不符)
            score_map = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}
            # 提取选项的第一个字母 (比如 "A. 经常" -> "A")
            choice = answer_text[0] 
            points = score_map.get(choice, 0)
            
            # 累加分数
            if dim in scores:
                scores[dim] += points
                
    return scores