import streamlit as st
import logic # 引入我们的大脑

import plotly.graph_objects as go  # 记得在文件最上面加这一行

import os # <--- 【修改点1】引入os模块，用于检查本地图片是否存在
import database # 引入数据库操作模块
import pandas as pd

# 兼容性处理：旧版本 streamlit 使用 experimental_rerun
if not hasattr(st, 'rerun'):
    st.rerun = st.experimental_rerun
#一行注释
# 初始化数据库
database.init_db()

# 1. 页面基础设置 (必须是第一行)
st.set_page_config(
    page_title="CyberTCM 赛博本草",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 16Personalities Style CSS ---
st.markdown("""
<style>
/* 全局背景 - 简化渐变 */
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

/* 标题样式 - 使用系统字体 */
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

/* 所有p标签文字颜色为黑色 */
p, .stMarkdown p {
    color: #1A202C !important;
}

/* Plotly图表 - 简化选择器 */
.js-plotly-plot text {
    fill: #1A202C !important;
}

/* 问卷选项 - 黑色 */
[data-testid="stRadio"] label div,
[data-testid="stRadio"] label span,
.st-dg.st-dt,
[data-baseweb="radio"] div {
    font-size: 1rem !important;
    color: #1A202C !important;
}

/* 单选按钮标签 */
[role="radiogroup"] label {
    font-size: 1rem !important;
    color: #1A202C !important;
}

/* 自定义单选按钮样式 - 圆角方形风格 */
[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child {
    border-radius: 6px !important;
    border: 2px solid #48BB78 !important;
    background: white !important;
    width: 20px !important;
    height: 20px !important;
    position: relative !important;
}

/* 单选按钮内部隐藏默认样式 */
[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child > div {
    display: none !important;
}

/* 单选按钮选中状态 - 绿紫渐变 */
[data-testid="stRadio"] [data-baseweb="radio"] [aria-checked="true"] > div:first-child,
[data-testid="stRadio"] [data-baseweb="radio"][aria-checked="true"] > div:first-child {
    background: linear-gradient(135deg, #48BB78 0%, #805AD5 100%) !important;
    border-color: #805AD5 !important;
}

/* 单选按钮选中状态 - 白色小圆点 */
[data-testid="stRadio"] [data-baseweb="radio"] [aria-checked="true"] > div:first-child::after,
[data-testid="stRadio"] [data-baseweb="radio"][aria-checked="true"] > div:first-child::after {
    content: '' !important;
    position: absolute !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    width: 8px !important;
    height: 8px !important;
    background: white !important;
    border-radius: 50% !important;
}

/* 单选按钮悬停效果 */
[data-testid="stRadio"] [data-baseweb="radio"]:hover > div:first-child {
    border-color: #9F7AEA !important;
    box-shadow: 0 0 0 3px rgba(72, 187, 120, 0.3) !important;
}

/* 按钮样式 - 简化 */
.stButton > button {
    background: #805AD5 !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    font-weight: 700 !important;
    padding: 12px 24px !important;
}

/* Expander按钮样式 - 简化 */
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

/* Expander展开后的内容区域样式 */
[data-testid="stExpander"] details[open] {
    background: #f5f7fa !important;
    border-radius: 12px !important;
    padding: 15px !important;
    margin-top: 10px !important;
}

/* 统计数据卡片数字 */
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

/* 导航按钮容器 */
.nav-container {
    background: white;
    border-radius: 16px;
    padding: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    margin: 0 auto 30px auto;
    max-width: 800px;
}

/* 按钮样式 */
div.stButton > button {
    background: linear-gradient(135deg, #9F7AEA 0%, #805AD5 100%);
    color: white;
    border: none;
    border-radius: 50px;
    font-weight: 700;
    font-size: 0.95rem;
    padding: 12px 24px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(159, 122, 234, 0.4);
}

div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(159, 122, 234, 0.5);
}

div.stButton > button:active {
    transform: translateY(0);
}

/* 次要按钮 */
div.stButton > button[kind="secondary"] {
    background: #EDF2F7;
    color: #4A5568;
    box-shadow: none;
}

div.stButton > button[kind="secondary"]:hover {
    background: #E2E8F0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

/* 输入框样式 - 白色到蓝色渐变背景 */
.stTextInput > div > div > input {
    border-radius: 12px;
    border: 2px solid #E2E8F0;
    padding: 12px 16px;
    font-size: 1rem;
    transition: all 0.3s ease;
    background: linear-gradient(135deg, #FFFFFF 0%, #EBF8FF 50%, #E0F2FE 100%) !important;
    color: #1A202C !important;
}

.stTextInput > div > div > input:focus {
    border-color: #9F7AEA;
    box-shadow: 0 0 0 3px rgba(159, 122, 234, 0.1);
    background: linear-gradient(135deg, #FFFFFF 0%, #E6FFFA 50%, #B2F5EA 100%) !important;
}

/* 卡片样式 */
.stForm {
    background: white;
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

/* 警告样式 */
.stAlert {
    border-radius: 12px;
    border: none;
}

.stAlert[data-baseweb="notification"] {
    background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
    color: #92400E;
}

/* 成功样式 */
.stSuccess {
    border-radius: 12px;
    background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
    color: #065F46;
}

/* 错误样式 */
.stError {
    border-radius: 12px;
    background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
    color: #991B1B;
}

/* 信息样式 */
.stInfo {
    border-radius: 12px;
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
    transition: all 0.3s ease;
    text-decoration: none;
    box-shadow: 0 4px 15px rgba(159, 122, 234, 0.4);
    margin-top: 20px;
}

.back-to-top-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(159, 122, 234, 0.5);
}

/* 单选按钮样式 */
stRadio > div {
    background: white;
    border-radius: 12px;
    padding: 10px;
}

/* 滑块样式 */
.stSlider > div > div > div {
    background: #9F7AEA;
}

/* 表格样式 */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}

/* 隐藏streamlit默认元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* 响应式设计 */
@media (max-width: 768px) {
    h1 {
        font-size: 1.8rem !important;
    }
    
    .nav-container {
        padding: 8px;
    }
    
    div.stButton > button {
        font-size: 0.85rem;
        padding: 10px 16px;
    }
}
</style>
""", unsafe_allow_html=True)

# 添加页面顶部锚点
st.markdown("<div id='top'></div>", unsafe_allow_html=True)

# 版本信息
st.markdown("<div class='version-info'>v0.1 Alpha</div>", unsafe_allow_html=True)

# 3. 主界面：标题
st.title("🧬 TCM-BTI")
st.title("你的专属体质说明书")
st.markdown("<p class='subtitle'>✨ 61题内测版 预计7-8分钟完成</p>", unsafe_allow_html=True)


# 输入ID区域
st.markdown("<div style='max-width: 500px; margin: 0 auto 30px auto;'>", unsafe_allow_html=True)
user_name = st.text_input("输入您的代号 (ID):", "", placeholder="请输入您的昵称")

# 昵称验证
if not user_name:
    st.error("⚠️ 请输入昵称后再继续")
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

# 导航按钮区域
st.markdown("<div class='nav-container'>", unsafe_allow_html=True)
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
st.markdown("</div>", unsafe_allow_html=True)

# --- 模块 1: 问卷区 (双盲合并版) ---
if st.session_state["active_tab"] == 0:
    st.header("🧬 体质评估问卷")
    
    # 检查昵称是否已输入
    if 'nickname_valid' not in locals() or not nickname_valid:
        st.warning("⚠️ 请先在上方输入您的昵称")
        st.stop()
    
    # 加载两组题目
    df_questions = logic.load_questions()  # 28题
    df_wjw = logic.load_wjw_data()  # 33题
    
    if df_questions is None or df_wjw is None:
        st.error("❌ 无法加载题库，请检查数据库文件")
        st.stop()
    
    # 合并题目（不告诉用户来源）
    total_questions = len(df_questions) + len(df_wjw)
    st.info(f"📋 共 {total_questions} 道题目，请根据您的实际情况选择")
    
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
            # 1. 计算八纲辨证结果
            df_questions, df_types = logic.load_data()
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
                
                st.success("✅ 数据已同步到赛博数据库！")
            
            st.success("✅ 体质评估完成！")
            st.success("🎉 完整的体质报告已生成！现在回到点击体制报告按钮查看吧！")
            
            # 添加回到顶部按钮
            st.markdown("""
            <a href="#top" class="back-to-top-btn">⬆ 回到顶部</a>
            """, unsafe_allow_html=True)
            
            st.balloons()

# --- 模块 2: 视觉区 ---
elif st.session_state["active_tab"] == 1:
    st.header("第三阶段: 生物特征识别")
    
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
        st.subheader("🧬 八纲辨证体质")
        
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
            st.warning("⚠️ 尚未完成八纲辨证体质评估")
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
    
    # --- 保存完整数据到数据库 ---
    if part1_done and part2_done:
        if st.button("💾 保存完整报告到数据库", type="primary", use_container_width=True):
            with st.spinner("正在保存数据..."):
                # 提取两部分答案
                part1_answers = {}
                part2_answers = {}
                for key, value in st.session_state.items():
                    if key.startswith("q_"):
                        part1_answers[key] = value
                    elif key.startswith("wjw_q_"):
                        part2_answers[key] = value
                
                # 收集所有原始答案
                raw_answers = {}
                for key, value in st.session_state.items():
                    if key.startswith("q_") or key.startswith("wjw_q_"):
                        raw_answers[key] = value
                
                # 保存完整数据
                database.save_complete_questionnaire(
                    user_id=st.session_state["user_id"],
                    part1_result=st.session_state["part1_result"],
                    part2_result=st.session_state["part2_result"],
                    part1_answers=part1_answers,
                    part2_answers=part2_answers,
                    raw_answers=raw_answers
                )
                st.success("✅ 完整报告已保存到数据库！")
    
    # --- 详细结果展示 ---
    if part1_done and st.session_state.get("part1_result"):
        with st.expander("📊 点击查看详细结果"):
            res = st.session_state["part1_result"]
            
            # 双向能量条
            st.write("**⚡ 能量对抗监测**")
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