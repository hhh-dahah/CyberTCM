import streamlit as st
import logic # 引入我们的大脑

import plotly.graph_objects as go  # 记得在文件最上面加这一行

import os # <--- 【修改点1】引入os模块，用于检查本地图片是否存在
import database # 引入数据库操作模块
import pandas as pd

# 使用 PostgreSQL 数据库（Supabase）
from database_postgres import (
    init_db, get_or_create_user, save_complete_questionnaire,
    verify_admin_password, update_admin_password,
    get_statistics, search_questionnaires, export_to_excel
)

# # 注释掉旧的 SQLite 导入
# # from database import (
# #     init_db, get_or_create_user, save_complete_questionnaire,
# #     verify_admin_password, update_admin_password,
# #     get_statistics, search_questionnaires, export_to_excel
# # )

# # 使用 Supabase 导入
# # from database_supabase import (
# #     init_db, get_or_create_user, save_complete_questionnaire,
# #     verify_admin_password, update_admin_password,
# #     get_statistics, search_questionnaires, export_to_excel
# # )

# 兼容性处理：旧版本 streamlit 使用 experimental_rerun
if not hasattr(st, 'rerun'):
    st.rerun = st.experimental_rerun
#一行注释

# ==================== 性能优化：缓存数据加载 ====================
@st.cache_data(ttl=3600, show_spinner=False)
def load_questions_cached():
    """缓存加载问题数据，避免每次重新读取Excel"""
    return logic.load_questions()

@st.cache_data(ttl=3600, show_spinner=False)
def load_wjw_data_cached():
    """缓存加载卫健委数据"""
    return logic.load_wjw_data()

@st.cache_data(ttl=3600, show_spinner=False)
def load_data_cached():
    """缓存加载体质类型数据"""
    return logic.load_data()

# ==================== 性能优化：延迟初始化数据库 ====================
if "db_initialized" not in st.session_state:
    database.init_db()
    st.session_state["db_initialized"] = True

# 1. 页面基础设置 (必须是第一行)
st.set_page_config(
    page_title="CyberTCM 赛博本草",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 16Personalities Style CSS (性能优化：精简CSS) ---
st.markdown("""
<style>
/* 全局背景 */
.stApp {
    background: #F0F9FF;
}

/* 隐藏侧边栏 */
[data-testid="stSidebar"] {
    display: none !important;
}

/* 主内容区域 */
.main .block-container {
    max-width: 900px !important;
    padding: 20px !important;
}

/* 标题样式 */
h1 {
    color: #2D3748 !important;
    font-weight: 800 !important;
    font-size: 2.5rem !important;
    text-align: center;
    margin-bottom: 8px !important;
}

h2, h3 {
    color: #4A5568 !important;
    font-weight: 700 !important;
}

/* 文字颜色 */
p, .stMarkdown p {
    color: #1A202C !important;
}

/* Plotly图表 */
.js-plotly-plot text {
    fill: #1A202C !important;
}

/* 问卷选项 */
[data-testid="stRadio"] label div,
[data-testid="stRadio"] label span {
    font-size: 1rem !important;
    color: #1A202C !important;
}

[role="radiogroup"] label {
    font-size: 1rem !important;
    color: #1A202C !important;
}

/* 单选按钮样式 */
[data-testid="stRadio"] {
    all: unset !important;
    display: block !important;
}

[data-testid="stRadio"] > div {
    all: unset !important;
    display: flex !important;
    gap: 12px !important;
    flex-wrap: wrap !important;
}

[data-testid="stRadio"] > div > div {
    all: unset !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    cursor: pointer !important;
}

[data-testid="stRadio"] > div > div > div {
    all: unset !important;
    display: inline-block !important;
    width: 20px !important;
    height: 20px !important;
    border: 2px solid #CBD5E0 !important;
    border-radius: 50% !important;
    background: white !important;
    transition: all 0.2s ease !important;
}

[data-testid="stRadio"] > div > div[aria-checked="true"] > div {
    background: #48BB78 !important;
    border-color: #48BB78 !important;
}

[data-testid="stRadio"] > div > div:hover > div {
    border-color: #48BB78 !important;
}

[data-testid="stRadio"] > div > div > label {
    all: unset !important;
    font-size: 1rem !important;
    color: #1A202C !important;
    cursor: pointer !important;
}

/* 按钮样式 */
.stButton > button {
    background: #805AD5 !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    font-weight: 700 !important;
    padding: 12px 24px !important;
}

div.stButton > button {
    background: linear-gradient(135deg, #9F7AEA 0%, #805AD5 100%);
    color: white;
    border: none;
    border-radius: 50px;
    font-weight: 700;
    font-size: 0.95rem;
    padding: 12px 24px;
    transition: transform 0.2s ease;
    box-shadow: 0 4px 15px rgba(159, 122, 234, 0.4);
}

div.stButton > button:hover {
    transform: translateY(-2px);
}

div.stButton > button[kind="secondary"] {
    background: #EDF2F7;
    color: #4A5568;
    box-shadow: none;
}

/* Expander样式 */
[data-testid="stExpander"] details summary {
    background: #667eea !important;
    border-radius: 12px !important;
    padding: 12px 20px !important;
    border: none !important;
    cursor: pointer !important;
}

[data-testid="stExpander"] details summary p {
    color: white !important;
    font-weight: 600 !important;
    margin: 0 !important;
}

[data-testid="stExpander"] details[open] {
    background: #f5f7fa !important;
    border-radius: 12px !important;
    padding: 15px !important;
    margin-top: 10px !important;
}

/* 统计数据 */
[data-testid="stMetricValue"] {
    font-weight: 700 !important;
    color: #1A202C !important;
}

/* 副标题 */
.subtitle {
    text-align: center;
    color: #718096;
    font-size: 1.1rem;
    margin-bottom: 30px;
}

/* 版本信息 */
.version-info {
    position: absolute;
    top: 20px;
    left: 20px;
    font-size: 0.75rem;
    color: #A0AEC0;
    background: rgba(255,255,255,0.8);
    padding: 4px 12px;
    border-radius: 20px;
}

/* 加入我们按钮 - 闪动效果 */
.join-us-btn {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 50%, #FF6B6B 100%);
    background-size: 200% 200%;
    color: white;
    padding: 10px 20px;
    border-radius: 25px;
    font-weight: 700;
    font-size: 0.9rem;
    text-decoration: none;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    cursor: pointer;
    border: none;
    animation: pulse-glow 2s ease-in-out infinite, gradient-shift 3s ease infinite;
    transition: transform 0.2s ease;
}

.join-us-btn:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 6px 20px rgba(255, 107, 107, 0.6);
}

@keyframes pulse-glow {
    0%, 100% {
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    }
    50% {
        box-shadow: 0 4px 25px rgba(255, 107, 107, 0.8), 0 0 30px rgba(255, 107, 107, 0.4);
    }
}

@keyframes gradient-shift {
    0% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
    100% {
        background-position: 0% 50%;
    }
}

/* 导航按钮容器 */
.nav-container {
    background: white;
    border-radius: 16px;
    padding: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    margin: 0 auto 30px auto;
    max-width: 800px;
}

/* 输入框样式 */
.stTextInput > div > div > input {
    border-radius: 12px;
    border: 2px solid #E2E8F0;
    padding: 12px 16px;
    font-size: 1rem;
    background: linear-gradient(135deg, #FFFFFF 0%, #EBF8FF 50%, #E0F2FE 100%) !important;
    color: #1A202C !important;
}

.stTextInput > div > div > input:focus {
    border-color: #9F7AEA;
    box-shadow: 0 0 0 3px rgba(159, 122, 234, 0.1);
}

/* 卡片样式 */
.stForm {
    background: white;
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

/* 提示样式 */
.stAlert, .stSuccess, .stError, .stInfo {
    border-radius: 12px;
    border: none;
}

.stSuccess {
    background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
    color: #065F46;
}

.stError {
    background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
    color: #991B1B;
}

.stInfo {
    background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
    color: #1E40AF;
}

/* 分隔线 */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #E2E8F0, transparent);
    margin: 30px 0;
}

/* 回到顶部按钮 */
.back-to-top-btn {
    display: inline-block;
    background: linear-gradient(135deg, #9F7AEA 0%, #805AD5 100%);
    color: white;
    border: none;
    border-radius: 50px;
    padding: 14px 28px;
    font-weight: 700;
    font-size: 1rem;
    cursor: pointer;
    text-decoration: none;
    box-shadow: 0 4px 15px rgba(159, 122, 234, 0.4);
    margin-top: 20px;
}

.back-to-top-btn:hover {
    transform: translateY(-2px);
}

/* 滑块和表格 */
.stSlider > div > div > div {
    background: #9F7AEA;
}

.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}

/* 隐藏streamlit默认元素 */
#MainMenu, footer, header {visibility: hidden;}

/* 响应式设计 */
@media (max-width: 768px) {
    h1 { font-size: 1.8rem !important; }
    .nav-container { padding: 8px; }
    div.stButton > button { font-size: 0.85rem; padding: 10px 16px; }
    [data-testid="stRadio"] label { font-size: 1.2rem !important; }
    .stMarkdown p { font-size: 1.1rem !important; line-height: 1.6 !important; }
}
</style>
""", unsafe_allow_html=True)

# 初始化页面状态
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "main"

# 添加页面顶部锚点
st.markdown("<div id='top'></div>", unsafe_allow_html=True)

# 版本信息
st.markdown("<div class='version-info'>v1.0 Alpha</div>", unsafe_allow_html=True)

# 加入我们按钮区域 - 只在主页面显示
if st.session_state["current_page"] == "main":
    # 使用列布局创建右上角动态人物区域
    header_cols = st.columns([3, 1])
    with header_cols[1]:
        # 使用st.image显示GIF动图（确保动画播放）
        import base64
        with open("assets/doro.gif", "rb") as f:
            gif_data = f.read()
        gif_base64 = base64.b64encode(gif_data).decode()
        
        # GIF图片区域 - 长方形，完整显示
        st.markdown(f"""
        <style>
        .gif-wrapper {{
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 5px;
        }}
        .gif-container {{
            width: auto;
            height: auto;
            max-width: 150px;
            border-radius: 12px;
            overflow: hidden;
            border: 4px dashed rgba(102, 126, 234, 0.6);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
            animation: mascot-bounce 2s ease-in-out infinite;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 4px;
        }}
        .gif-container img {{
            width: 100%;
            height: auto;
            object-fit: contain;
            border-radius: 8px;
            display: block;
        }}
        @keyframes mascot-bounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-10px); }}
        }}
        </style>
        <div class="gif-wrapper">
            <div class="gif-container" title="点击加入我们">
                <img src="data:image/gif;base64,{gif_base64}" alt="点击加入我们">
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 红色按钮作为跳转开关
        st.markdown("""
        <style>
        div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:first-child div[data-testid="column"]:nth-child(2) button {
            background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 20px !important;
            font-weight: 700 !important;
            font-size: 0.85rem !important;
            padding: 12px 20px !important;
            box-shadow: 0 6px 20px rgba(255, 107, 107, 0.5) !important;
            animation: sign-pulse 2s ease-in-out infinite !important;
            text-align: center !important;
            line-height: 1.4 !important;
            white-space: nowrap !important;
            min-width: 140px !important;
        }
        @keyframes sign-pulse {
            0%, 100% { box-shadow: 0 6px 20px rgba(255, 107, 107, 0.5); }
            50% { box-shadow: 0 8px 30px rgba(255, 107, 107, 0.9); }
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("项目招人中\n点击加入我们", key="join_us_btn"):
            st.session_state["current_page"] = "join_us"
            st.rerun()

# ==================== 主页面内容 ====================
if st.session_state["current_page"] == "main":
    # 3. 主界面：标题
    st.title("🧬 PBTI")
    st.title("你的专属体质说明书")
    st.markdown("<p class='subtitle'>✨ 61题内测版 预计5-8分钟完成</p>", unsafe_allow_html=True)


    # 输入ID区域
    st.markdown("<div style='max-width: 500px; margin: 0 auto 30px auto;'>", unsafe_allow_html=True)
    user_name = st.text_input("输入您的代号 (ID):", "", placeholder="输入昵称后点击空白处继续")

    # 昵称验证
    if not user_name:
        st.error("⚠️ 输入昵称后点击空白处能查看问卷")
        nickname_valid = False
    else:
        st.success(f"欢迎回来, {user_name} 👋")
        nickname_valid = True
        
        # 获取或创建用户
        user_id = database.get_or_create_user(user_name)
        st.session_state["user_id"] = user_id
        st.session_state["nickname"] = user_name
    st.markdown("</div>", unsafe_allow_html=True)

    # 4. 核心功能区 (用 Tabs 分页)
    # 初始化活动标签页
    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = 0

    # 初始化问卷完成状态
    if "part1_completed" not in st.session_state:
        st.session_state["part1_completed"] = False
    if "part2_completed" not in st.session_state:
        st.session_state["part2_completed"] = False
    if "part1_result" not in st.session_state:
        st.session_state["part1_result"] = None
    if "part2_result" not in st.session_state:
        st.session_state["part2_result"] = None

    # 导航按钮区域 - 分两行显示
    st.markdown("<div class='nav-container'>", unsafe_allow_html=True)
    
    # 第一行：4个主要功能按钮
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🧬 体质问卷", use_container_width=True, 
                     type="primary" if st.session_state["active_tab"] == 0 else "secondary"):
            st.session_state["active_tab"] = 0
            st.rerun()
    with col2:
        if st.button("📸 舌象解码", use_container_width=True,
                     type="primary" if st.session_state["active_tab"] == 1 else "secondary"):
            st.session_state["active_tab"] = 1
            st.rerun()
    with col3:
        if st.button("🔮 体质报告", use_container_width=True,
                     type="primary" if st.session_state["active_tab"] == 2 else "secondary"):
            st.session_state["active_tab"] = 2
            st.rerun()
    with col4:
        if st.button("📊 数据管理", use_container_width=True,
                     type="primary" if st.session_state["active_tab"] == 3 else "secondary"):
            st.session_state["active_tab"] = 3
            st.rerun()
    
    # 第二行：加入我们按钮（居中显示）
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        if st.button("🎉 加入我们", use_container_width=True, type="secondary"):
            st.session_state["current_page"] = "join_us"
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

    # --- 模块 1: 问卷区 (双盲合并版) ---
    if st.session_state["active_tab"] == 0:
        st.header("🧬 体质评估问卷")
        
        # 检查昵称是否已输入
        if 'nickname_valid' not in locals() or not nickname_valid:
            st.warning("⚠️ 请先在上方输入您的昵称")
            st.stop()
        
        # 加载两组题目（使用缓存函数提升性能）
        df_questions = load_questions_cached()  # 28题
        df_wjw = load_wjw_data_cached()  # 33题
        
        if df_questions is None or df_wjw is None:
            st.error("❌ 无法加载题库，请检查数据库文件")
            st.stop()
        
        # 合并题目（不告诉用户来源）
        total_questions = len(df_questions) + len(df_wjw)
        st.info(f"📋 共 {total_questions} 道题目，内设逻辑判断 乱选可能导致全部数据作废")
        st.info(f"📋 温馨提示：问卷初始默认选C 点击选项可改变选择")
        
        # 创建合并表单
        with st.form("combined_quiz_form"):
            # 第一组题目（28题）- 不显示来源
            for index, row in df_questions.iterrows():
                question_number = index + 1
                st.write(f"**{question_number}. {row['question']}**")
                st.radio(
                    "请选择程度:", 
                    ["A. 非常符合", "B. 比较符合", "C. 一般", "D. 不太符合", "E. 完全不符"],
                    key=f"q_{row['id']}",
                    index=2,
                    horizontal=True,
                    label_visibility="collapsed"
                )
                st.markdown("---")
            
            # 第二组题目（33题）- 不显示来源，题号连续
            for index, row in df_wjw.iterrows():
                question_number = len(df_questions) + index + 1
                st.write(f"**{question_number}. {row['question']}**")
                st.radio(
                    "请选择程度:",
                    ["A. 非常符合", "B. 比较符合", "C. 一般", "D. 不太符合", "E. 完全不符"],
                    key=f"wjw_q_{row['id']}",
                    index=2,
                    horizontal=True,
                    label_visibility="collapsed"
                )
                st.markdown("---")
            
            # 提交按钮
            submitted = st.form_submit_button("🚀 提交问卷", type="primary")
        
        if submitted:
            with st.spinner("正在分析您的体质数据..."):
                # 1. 计算PBTI体质结果（使用缓存函数）
                df_questions, df_types = load_data_cached()
                result_part1 = logic.calculate_results(st.session_state, df_questions, df_types)
                st.session_state["part1_result"] = result_part1
                st.session_state["part1_completed"] = True
                
                # 2. 计算卫健委体质结果
                result_part2 = logic.calculate_wjw_results(st.session_state, df_wjw)
                st.session_state["part2_result"] = result_part2
                st.session_state["part2_completed"] = True
                
                # 3. 存储到数据库
                if "user_id" in st.session_state:
                    user_id = st.session_state["user_id"]
                    
                    # 提取两部分答案
                    part1_answers = {}
                    part2_answers = {}
                    raw_answers = {}
                    for key, value in st.session_state.items():
                        if key.startswith("q_"):
                            part1_answers[key] = value
                            raw_answers[key] = value
                        elif key.startswith("wjw_q_"):
                            part2_answers[key] = value
                            raw_answers[key] = value
                    
                    # 保存完整数据
                    database.save_complete_questionnaire(
                        user_id=user_id,
                        part1_result=result_part1,
                        part2_result=result_part2,
                        part1_answers=part1_answers,
                        part2_answers=part2_answers,
                        raw_answers=raw_answers
                    )
                    
                    # st.success("✅ 数据已同步到赛博数据库！")
                
                st.success("✅ 体质评估完成！感谢您对健康科研事业的贡献！😆")
                st.success("🎉 完整的体质报告已生成！现在回到点击'体质报告' 按钮查看吧！")
                
                # 添加回到顶部按钮
                st.markdown("""
                <a href="#top" class="back-to-top-btn">⬆ 回到顶部</a>
                """, unsafe_allow_html=True)
                
                st.balloons()

    # --- 模块 2: 视觉区 ---
    elif st.session_state["active_tab"] == 1:
        st.header("第三阶段: 生物特征识别 (功能尚未完善 请跳过该部分)")
        
        # 检查昵称是否已输入
        if 'nickname_valid' not in locals() or not nickname_valid:
            st.warning("⚠️ 请先在上方输入您的昵称")
            st.stop()
        
        st.warning("⚠️ 请在光线充足环境下拍摄舌象")
        
        # 上传组件
        uploaded_file = st.file_uploader("上传舌头照片", type=['jpg', 'png'])
        if uploaded_file:
            st.image(uploaded_file, caption="样本采集成功", width=300)
            
            # 添加回到顶端按钮
            st.markdown("""
            <a href="#top" class="back-to-top-btn">⬆ 回到顶端</a>
            """, unsafe_allow_html=True)

    # --- 模块 4: 结果区 ---
    elif st.session_state["active_tab"] == 2:
        # 检查昵称是否已输入
        if 'nickname_valid' not in locals() or not nickname_valid:
            st.warning("⚠️ 请先在上方输入您的昵称")
            st.stop()
        
        # 检查是否两部分都已完成
        part1_done = st.session_state.get("part1_completed", False)
        part2_done = st.session_state.get("part2_completed", False)
        
        if not part1_done and not part2_done:
            st.info("👈 请先在上方完成【体质问卷】以解锁数据")
            st.stop()
        
        st.header("🔮 您的完整体质报告")
        
        # 创建两列显示两种体质结果
        col_part1, col_part2 = st.columns(2)
        
        # --- 第一部分：八纲辨证体质结果 ---
        with col_part1:
            st.subheader("🧬 PBTI体质（实验中）")
            
            if part1_done and st.session_state.get("part1_result"):
                res = st.session_state["part1_result"]
                info = res["user_info"]
                badge = res["social_badge"]
                
                st.markdown(f"**{info['type_code']} · {info['type_name']}**")
                
                # 判词
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #E9D8FD 0%, #D6BCFA 100%); padding: 15px; border-radius: 12px; border-left: 4px solid #805AD5;">
                    <p style="color: #553C9A; font-size: 0.95em; margin: 0; font-style: italic;">"{badge['poem']}"</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 雷达图
                radar_data = res["radar_chart"]
                categories = ['寒','热','虚','实','燥','湿','郁','瘀']
                values = [radar_data['cold'], radar_data['heat'], radar_data['void'], radar_data['solid'], 
                          radar_data['dry'], radar_data['wet'], radar_data['qi'], radar_data['blood']]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name=info['type_name'],
                    line_color='#805AD5',
                    fillcolor='rgba(128, 90, 213, 0.3)'
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color="#4A5568",
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.warning("⚠️ 尚未完成PBTI体质评估")
                if st.button("🧬 去完成28题评估", key="goto_part1"):
                    st.session_state["active_tab"] = 0
                    st.rerun()
        
        # --- 第二部分：卫健委9种体质结果 ---
        with col_part2:
            st.subheader("🏥 卫健委9种体质")
            
            if part2_done and st.session_state.get("part2_result"):
                wjw_res = st.session_state["part2_result"]
                
                st.markdown(f"**主要体质：{wjw_res['main_constitution']}**")
                st.markdown(f"得分：{wjw_res['main_score']} 分 | 判定：{wjw_res['main_result']}")
                
                # 显示所有体质得分表格
                st.markdown("**各体质详细得分：**")
                for constitution, result in wjw_res['constitution_results'].items():
                    if result['result'] in ['是', '基本是']:
                        st.success(f"{constitution}: {result['score']}分 - {result['result']}")
                    elif result['result'] == '倾向是':
                        st.warning(f"{constitution}: {result['score']}分 - {result['result']}")
                    else:
                        st.caption(f"{constitution}: {result['score']}分 - {result['result']}")
            else:
                st.warning("⚠️ 尚未完成卫健委体质评估")
                if st.button("🏥 去完成33题评估", key="goto_part2"):
                    st.session_state["active_tab"] = 1
                    st.rerun()
        
        st.divider()
        
        # --- 详细结果展示 ---
        if part1_done and st.session_state.get("part1_result"):
            with st.expander("📊 点击查看详细结果"):
                res = st.session_state["part1_result"]
                
                # 双向能量条
                st.write("**⚡ 体质偏颇监测**")
                for bar in res["energy_bars"]:
                    st.write(f"{bar['left']} ⟵ VS ⟶ {bar['right']}")
                    st.slider(
                        label="hidden", 
                        min_value=-100, max_value=100, value=int(bar['val']), 
                        disabled=True, 
                        key=f"detail_{bar['label']}"
                    )
                
                # 行动指南
                st.subheader("🚀 调优方案")
                ac_col1, ac_col2, ac_col3 = st.columns(3)
                with ac_col1:
                    st.success("**Keep 保持**")
                    for item in res['action_guide']['keep']:
                        st.write(f"✅ {item}")
                with ac_col2:
                    st.warning("**Stop 停止**")
                    for item in res['action_guide']['stop']:
                        st.write(f"🛑 {item}")
                with ac_col3:
                    st.info("**Start 开始**")
                    for item in res['action_guide']['start']:
                        st.write(f"🚀 {item}")
        
        # 添加回到顶端按钮
        st.markdown("""
        <a href="#top" class="back-to-top-btn">⬆ 回到顶端</a>
        """, unsafe_allow_html=True)

    # --- 模块 5: 数据管理区 (管理员专用) ---
    elif st.session_state["active_tab"] == 3:
        st.header("📊 赛博数据中心")
        st.markdown("*管理员专用 - 管理和导出体质数据*")
        
        # 初始化管理员登录状态
        if "admin_logged_in" not in st.session_state:
            st.session_state["admin_logged_in"] = False
        
        # 如果未登录，显示密码输入界面
        if not st.session_state["admin_logged_in"]:
            st.warning("⚠️ 此功能需要管理员权限")
            
            admin_password = st.text_input("请输入管理员密码", type="password", placeholder="默认密码: 8888")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("🔓 登录", type="primary"):
                    if database.verify_admin_password(admin_password):
                        st.session_state["admin_logged_in"] = True
                        st.success("✅ 登录成功！")
                        st.rerun()
                    else:
                        st.error("❌ 密码错误")
            
            st.info("💡 提示：默认密码登录后可在设置中修改")
        
        # 如果已登录，显示数据管理内容
        else:
            # 显示登出按钮和修改密码选项
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🚪 退出登录"):
                    st.session_state["admin_logged_in"] = False
                    st.rerun()
            with col2:
                with st.expander("🔧 修改密码"):
                    current_pwd = st.text_input("当前密码", type="password")
                    new_pwd = st.text_input("新密码", type="password")
                    confirm_pwd = st.text_input("确认新密码", type="password")
                    
                    if st.button("💾 确认修改"):
                        if not current_pwd or not new_pwd or not confirm_pwd:
                            st.error("❌ 请填写所有密码字段")
                        elif new_pwd != confirm_pwd:
                            st.error("❌ 两次输入的新密码不一致")
                        elif len(new_pwd) < 4:
                            st.error("❌ 新密码长度至少为4位")
                        else:
                            success, message = database.update_admin_password(current_pwd, new_pwd)
                            if success:
                                st.success(f"✅ {message}")
                                st.info("请使用新密码重新登录")
                                st.session_state["admin_logged_in"] = False
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
            
            st.divider()
            
            # 数据统计概览
            st.subheader("📈 数据概览")
            
            try:
                stats = database.get_statistics()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("👥 总用户数", stats['total_users'])
                with col2:
                    st.metric("📝 总问卷数", stats['total_questionnaires'])
                with col3:
                    st.metric("📅 今日新增", stats['today_count'])
                
                # 体质类型分布
                if stats['type_distribution']:
                    st.subheader("🧬 体质类型分布")
                    
                    # 创建体质分布数据
                    type_data = pd.DataFrame(stats['type_distribution'])
                    
                    # 显示分布图表
                    fig = go.Figure(data=[
                        go.Bar(
                            x=type_data['type_name'],
                            y=type_data['count'],
                            marker_color='#805AD5'
                        )
                    ])
                    fig.update_layout(
                        title="体质类型统计",
                        xaxis_title="体质类型",
                        yaxis_title="数量",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color="#4A5568"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 显示详细数据表
                    st.dataframe(type_data, use_container_width=True)
                
                # 数据查询功能
                st.subheader("🔍 数据查询")
                
                # 搜索选项
                search_col1, search_col2, search_col3 = st.columns(3)
                with search_col1:
                    search_nickname = st.text_input("按昵称搜索", "")
                with search_col2:
                    search_type = st.selectbox("按体质类型", ["全部"] + [t['type_code'] for t in stats['type_distribution']])
                with search_col3:
                    date_range = st.date_input("日期范围", [])
                
                # 执行搜索
                if st.button("🔍 搜索"):
                    start_date = None
                    end_date = None
                    if len(date_range) == 2:
                        start_date = date_range[0].strftime('%Y-%m-%d')
                        end_date = date_range[1].strftime('%Y-%m-%d')
                    
                    type_code = None if search_type == "全部" else search_type
                    
                    results = database.search_questionnaires(
                        nickname=search_nickname if search_nickname else None,
                        type_code=type_code,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    if results:
                        st.success(f"找到 {len(results)} 条记录")
                        results_df = pd.DataFrame(results)
                        st.dataframe(results_df, use_container_width=True)
                    else:
                        st.info("未找到匹配的记录")
                
                # 数据导出功能
                st.subheader("💾 数据导出")
                
                export_col1, export_col2 = st.columns(2)
                with export_col1:
                    if st.button("📄 导出为 CSV"):
                        filename = database.export_to_csv()
                        st.success(f"✅ 数据已导出到: {filename}")
                        
                        # 提供下载链接
                        with open(filename, 'rb') as f:
                            st.download_button(
                                label="⬇️ 下载 CSV 文件",
                                data=f,
                                file_name=filename,
                                mime='text/csv'
                            )
                
                with export_col2:
                    if st.button("📊 导出为 Excel"):
                        filename = database.export_to_excel()
                        if filename:
                            st.success(f"✅ 数据已导出到: {filename}")
                            
                            # 提供下载链接
                            with open(filename, 'rb') as f:
                                st.download_button(
                                    label="⬇️ 下载 Excel 文件",
                                    data=f,
                                    file_name=filename,
                                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                                )
                        else:
                            st.error("❌ 导出失败，请确保已安装 pandas 和 openpyxl")
                
                # 显示所有问卷数据
                st.subheader("📋 所有问卷记录")
                
                all_questionnaires = database.get_all_questionnaires(limit=100)
                if all_questionnaires:
                    df = pd.DataFrame(all_questionnaires)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("暂无问卷数据")
                
                # 数据库信息
                st.subheader("🗄️ 数据库信息")
                
                db_info = database.get_database_info()
                if db_info:
                    st.write(f"**数据库文件**: {db_info['file_path']}")
                    st.write(f"**文件大小**: {db_info['file_size']}")
                    st.write(f"**数据表**: {', '.join(db_info['tables'])}")
                else:
                    st.info("数据库文件不存在")
                    
            except Exception as e:
                st.error(f"❌ 数据加载失败: {e}")
                st.info("💡 提示：如果数据库为空，请先完成一些问卷")

# ==================== 加入我们页面 ====================
elif st.session_state["current_page"] == "join_us":
    # 返回按钮
    col_back, col_title = st.columns([1, 5])
    with col_back:
        if st.button("⬅️ 返回", key="back_to_main"):
            st.session_state["current_page"] = "main"
            st.rerun()
    
    # 页面标题
    st.markdown("---")
    #st.header("✴️ 加入 CyberTCM 团队")
    #st.subheader("🚀 加入我们，一起探索中医智慧的未来！")
    
    # 招聘信息区域
    st.markdown("---")
    
    # 标题
    st.markdown("## 🎯 真实成果，留给实干者")
    st.markdown("""
    我们已经做出了真实成果，也愿意把机会给真正做事的人。
    
    我们是一个围绕知识库搭建的学生共创平台。目前已产出全栈网站与数据库系统，
    完成论文《养生文化与人格类型研究》。我们根据实际贡献提供署名机会，
    开放比赛核心团队位置，并持续为成员提供项目机会与技术支持。
    """)
    
    # 加入后获得
    st.markdown("### 📦 加入后获得")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **📂 项目参与**
        
        内部项目优先参与权，
        从概念到落地的完整实战机会
        """)
    with col2:
        st.markdown("""
        **💻 技术支撑**
        
        网站、小程序、系统开发支持，
        技术难题答疑与方案建议
        """)
    with col3:
        st.markdown("""
        **🤝 资源网络**
        
        跨专业人才组队通道，
        已有知识库与教程复用权限
        """)
    
    # 核心承诺
    st.markdown("### 🎖️ 核心承诺")
    st.info("只要产生实际贡献，即可获得：")
    
    promise_col1, promise_col2, promise_col3 = st.columns(3)
    with promise_col1:
        st.markdown("📝 **论文合作署名权**")
    with promise_col2:
        st.markdown("🏆 **项目核心成员身份**")
    with promise_col3:
        st.markdown("📌 **个人成果长期沉淀与展示**")
    
    # 我们在寻找
    st.markdown("### 👥 我们在寻找")
    
    st.error("🚫 **不是空想家** —— 只看不做的旁观者")
    st.success("✅ **而是实干者** —— 愿意把能力转化为真实结果的人")
    
    # 行动号召
    st.markdown("---")
    st.markdown("""
    ### 🚀 准备好将想法落地？
    
    **关注下方公众号，私信"加入我们"联系我们**
    """)
    
    # 联系方式 - 公众号二维码
    st.markdown("---")
    st.subheader("📮 联系我们")
    
    # 创建二维码展示区域
    col_qr1, col_qr2, col_qr3 = st.columns([1, 2, 1])
    with col_qr2:
        # 显示公众号二维码
        try:
            st.image("assets/account.jpg", width=250, caption="")
        except:
            st.error("无法加载二维码图片")
        
        # 文案 - 使用Streamlit原生组件
        st.info("📱 关注公众号，发送'加入项目'联系我们")
    
    # 底部返回按钮
    st.markdown("---")
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        if st.button("🏠 返回首页", type="primary", use_container_width=True):
            st.session_state["current_page"] = "main"
            st.rerun()