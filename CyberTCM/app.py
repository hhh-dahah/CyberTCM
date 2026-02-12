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
    layout="wide", # 宽屏模式，更像专业软件
    initial_sidebar_state="expanded"
)
# --- 🌑 修复版：图标清晰 + 呼吸感交互 ---
st.markdown("""
<style>
/* 1. 全局背景：深空黑 + 赛博点阵 */
.stApp {
    background-color: #0E1117;
    background-image: radial-gradient(rgba(0, 255, 200, 0.15) 1px, transparent 1px);
    background-size: 30px 30px;
}

/* 2. 核心修复：标题样式 (H1, H2, H3) */
/* 平时状态：纯白，看得清图标细节 */
h1, h2, h3 {
    color: #FFFFFF !important; 
    font-family: 'Courier New', sans-serif;
    font-weight: 800;
    text-shadow: 0 0 10px rgba(0, 255, 200, 0.3); /* 淡淡的绿光，证明系统是活的 */
    transition: all 0.3s ease; /* 0.3秒的丝滑过渡 */
    cursor: default; /* 鼠标放上去变成箭头 */
}

/* 悬停状态 (Hover)：瞬间变绿 + 爆闪 */
h1:hover, h2:hover, h3:hover {
    color: #00FFC8 !important; /* 荧光绿 */
    text-shadow: 
        0 0 20px rgba(0, 255, 200, 0.8),
        0 0 40px rgba(0, 255, 200, 0.4);
    transform: scale(1.01); /* 微微放大，像呼吸一样 */
}

/* 3. 侧边栏样式 */
[data-testid="stSidebar"] {
    background-color: #12141C; /* 比背景稍微亮一点的黑 */
    border-right: 1px solid rgba(0, 255, 200, 0.1);
}

/* 4. 卡片容器：黑钻质感 - 只应用于侧边栏 */
[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div {
    background-color: rgba(255, 255, 255, 0.03); /* 极淡的白透明 */
    border: 1px solid rgba(0, 255, 200, 0.2); 
    border-radius: 12px;
    padding: 20px;
    backdrop-filter: blur(5px);
    margin-bottom: 25px !important; /* 增加底部间距 */
    overflow: hidden; /* 防止内容溢出 */
}

/* 修复侧边栏内所有元素的间距问题 */
[data-testid="stSidebar"] .stTextInput,
[data-testid="stSidebar"] div[data-testid="stTextInput"] {
    margin-bottom: 15px !important;
    margin-top: 10px !important;
    position: relative;
    z-index: 1;
}

/* 修复输入框容器，防止溢出 */
[data-testid="stSidebar"] div[data-testid="stTextInput"] > div {
    padding: 0 !important;
    margin: 0 !important;
}

/* 修复输入框本身 */
[data-testid="stSidebar"] div[data-testid="stTextInput"] input {
    margin: 0 !important;
    position: relative;
    z-index: 1;
}

/* 修复输入框外层容器 */
[data-testid="stSidebar"] div[data-testid="stElementContainer"] {
    margin-bottom: 15px !important;
    position: relative;
}

[data-testid="stSidebar"] .stAlert,
[data-testid="stSidebar"] div[data-testid="stAlert"] {
    margin-top: 10px !important;
    margin-bottom: 15px !important;
}

[data-testid="stSidebar"] .stDivider,
[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] {
    margin-top: 20px !important;
    margin-bottom: 20px !important;
}

/* 确保侧边栏内的垂直块之间有足够的间距 */
[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
    gap: 20px !important;
}

/* 修复侧边栏内标签和输入框之间的间距 */
[data-testid="stSidebar"] .stMarkdown {
    margin-bottom: 10px !important;
}

/* 赛博风格回到顶端按钮 */
.back-to-top-btn {
    display: inline-block;
    background: transparent;
    border: 2px solid #00FFC8;
    border-radius: 8px;
    color: #00FFC8;
    padding: 12px 20px;
    font-family: 'Courier New', monospace;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 2px;
    text-decoration: none;
    margin-top: 20px;
}

.back-to-top-btn:hover {
    background: #00FFC8;
    color: #0E1117;
    box-shadow: 0 0 20px rgba(0, 255, 200, 0.6);
    transform: translateY(-2px);
}

/* 5. 按钮：平时空心，悬停实心 (更高级的赛博感) */
div.stButton > button {
    background-color: transparent;
    color: #00FFC8;
    border: 2px solid #00FFC8; /* 荧光描边 */
    border-radius: 8px;
    font-weight: bold;
    transition: all 0.3s;
}

div.stButton > button:hover {
    background-color: #00FFC8; /* 填满 */
    color: #0E1117; /* 字变黑 */
    box-shadow: 0 0 20px rgba(0, 255, 200, 0.6);
}

/* 6. 修复 st.info/st.success 的文字颜色 */
.stAlert {
    background-color: rgba(0, 255, 200, 0.1);
    color: #FFFFFF;
    border: 1px solid #00FFC8;
}
</style>
""", unsafe_allow_html=True)

# 添加页面顶部锚点
st.markdown("<div id='top'></div>", unsafe_allow_html=True)

# 2. 侧边栏：控制中心
with st.sidebar:
    st.title("🔋 能量控制台")
    st.info("系统版本: v0.1 Alpha")
    
    # 昵称输入（必填）
    user_name = st.text_input("输入代号 (ID):", "", placeholder="请输入您的昵称")
    
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
    
    st.write("🔧 调试工具")
    if st.button("清除缓存 (Reset)"):
        st.cache_data.clear()
        st.success("内存已释放")

# 3. 主界面：赛博标题
st.title("👾 TCM-BTI：你的赛博体质说明书")
st.markdown("##### *✨ 科学解码 · 国潮养生 · 寻找你的体质同类*")

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

tab_names = ["🧬 快速扫描 (28题)", "🏥 卫健委体质 (33题)", "📸 舌象解码 (AI)", "🔮 专属体质报告", "📊 数据管理"]

# 使用 radio 按钮作为标签导航，支持程序化切换
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

st.divider()

# --- 模块 1: 问卷区 (双盲合并版) ---
if st.session_state["active_tab"] == 0:
    st.header("🧬 体质评估问卷")
    
    # 检查昵称是否已输入
    if 'nickname_valid' not in locals() or not nickname_valid:
        st.warning("⚠️ 请先在左侧边栏输入您的昵称")
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
                ["A. 非常符合 (5分)", "B. 比较符合 (4分)", "C. 一般 (3分)", "D. 不太符合 (2分)", "E. 完全不符 (1分)"],
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
                ["A. 非常符合 (5分)", "B. 比较符合 (4分)", "C. 一般 (3分)", "D. 不太符合 (2分)", "E. 完全不符 (1分)"],
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
                for key, value in st.session_state.items():
                    if key.startswith("q_"):
                        part1_answers[key] = value
                    elif key.startswith("wjw_q_"):
                        part2_answers[key] = value
                
                # 保存完整数据
                database.save_complete_questionnaire(
                    user_id=user_id,
                    part1_result=result_part1,
                    part2_result=result_part2,
                    part1_answers=part1_answers,
                    part2_answers=part2_answers
                )
                
                st.success("✅ 数据已同步到赛博数据库！")
            
            st.success("✅ 体质评估完成！")
            st.success("🎉 完整的体质报告已生成！现在回到顶部查看吧！")
            
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
        st.warning("⚠️ 请先在左侧边栏输入您的昵称")
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
        st.warning("⚠️ 请先在左侧边栏输入您的昵称")
        st.stop()
    
    # 检查是否两部分都已完成
    part1_done = st.session_state.get("part1_completed", False)
    part2_done = st.session_state.get("part2_completed", False)
    
    if not part1_done and not part2_done:
        st.info("👈 请先在左侧完成【快速扫描(28题)】和【卫健委体质(33题)】以解锁数据")
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
            <div style="background: rgba(0,255,200,0.1); padding: 10px; border-radius: 8px; border-left: 3px solid #00FFC8;">
                <p style="color: #00FFC8; font-size: 0.9em; margin: 0;">"{badge['poem']}"</p>
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
                line_color='#00FFC8'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="white",
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
                
                # 保存完整数据
                database.save_complete_questionnaire(
                    user_id=st.session_state["user_id"],
                    part1_result=st.session_state["part1_result"],
                    part2_result=st.session_state["part2_result"],
                    part1_answers=part1_answers,
                    part2_answers=part2_answers
                )
                st.success("✅ 完整报告已保存到数据库！")
    
    # --- 详细结果展示 ---
    if part1_done and st.session_state.get("part1_result"):
        with st.expander("📊 查看八纲辨证详细结果"):
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
    st.header("� 赛博数据中心")
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
        
        st.info("💡 提示：默认密码为 8888，登录后可在设置中修改")
    
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
                        marker_color='#00FFC8'
                    )
                ])
                fig.update_layout(
                    title="体质类型统计",
                    xaxis_title="体质类型",
                    yaxis_title="数量",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color="white"
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