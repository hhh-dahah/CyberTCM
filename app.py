import streamlit as st
import logic # 引入我们的大脑

import plotly.graph_objects as go  # 记得在文件最上面加这一行

import os # <--- 【修改点1】引入os模块，用于检查本地图片是否存在
import pandas as pd

# 使用 PostgreSQL 数据库（Supabase）
from database_postgres import (
    init_db, get_or_create_user, save_complete_questionnaire,
    verify_admin_password, update_admin_password,
    get_statistics, search_questionnaires, export_to_excel,
    get_all_questionnaires
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
    init_db()
    st.session_state["db_initialized"] = True

# 1. 页面基础设置 (必须是第一行)
st.set_page_config(
    page_title="CyberTCM 赛博本草",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 自定义样式
def load_css():
    with open('.streamlit/style.css', encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 尝试加载CSS，如果失败则使用默认样式
try:
    load_css()
except:
    pass

# 3. 页面内容
st.markdown("<h1 class='main-title'>CyberTCM 赛博本草</h1>", unsafe_allow_html=True)
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
    user_id = get_or_create_user(user_name)
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
                try:
                    save_complete_questionnaire(
                        user_id=user_id,
                        part1_result=result_part1,
                        part2_result=result_part2,
                        part1_answers=part1_answers,
                        part2_answers=part2_answers,
                        raw_answers=raw_answers
                    )
                    st.success("✅ 数据已同步到赛博数据库！")
                except Exception as e:
                    st.error(f"❌ 数据保存失败: {e}")
                    import traceback
                    st.error(traceback.format_exc())
            
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
        st.subheader("🧬 PBTI 体质分析")
        
        if part1_done and st.session_state.get("part1_result"):
            result = st.session_state["part1_result"]
            
            # 显示体质类型
            user_info = result.get('user_info', {})
            st.markdown(f"""
            <div class="result-card">
                <h3>您的体质类型</h3>
                <div class="type-badge">{user_info.get('type_name', '未知')}</div>
                <p><strong>类型代码:</strong> {user_info.get('type_code', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 显示雷达图
            radar_data = result.get('radar_chart', {})
            if radar_data:
                import plotly.graph_objects as go
                
                categories = list(radar_data.keys())
                values = list(radar_data.values())
                
                fig = go.Figure(data=go.Scatterpolar(
                    r=values + [values[0]],  # 闭合图形
                    theta=categories + [categories[0]],
                    fill='toself',
                    name='体质分布'
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, max(values) * 1.2]
                        )),
                    showlegend=False,
                    title="体质分布雷达图",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color="#4A5568"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # 显示能量条
            energy_data = result.get('energy_bars', {})
            if energy_data:
                st.markdown("#### ⚡ 体质能量分布")
                for key, value in energy_data.items():
                    st.progress(min(value / 100, 1.0), text=f"{key}: {value}")
        else:
            st.info("请完成体质问卷以查看结果")
    
    # --- 第二部分：卫健委体质结果 ---
    with col_part2:
        st.subheader("🏥 卫健委体质分析")
        
        if part2_done and st.session_state.get("part2_result"):
            result = st.session_state["part2_result"]
            
            # 显示主要体质
            main_constitution = result.get('main_constitution', '未知')
            main_score = result.get('main_score', 0)
            main_result = result.get('main_result', '未知')
            
            st.markdown(f"""
            <div class="result-card">
                <h3>主要体质</h3>
                <div class="type-badge">{main_constitution}</div>
                <p><strong>得分:</strong> {main_score}</p>
                <p><strong>判定:</strong> {main_result}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 显示所有体质结果
            constitution_results = result.get('constitution_results', {})
            if constitution_results:
                st.markdown("#### 📊 各体质详细结果")
                for constitution, data in constitution_results.items():
                    score = data.get('score', 0)
                    result_type = data.get('result', '未知')
                    st.write(f"**{constitution}**: {score}分 - {result_type}")
        else:
            st.info("请完成体质问卷以查看结果")

# --- 模块 5: 数据管理 ---
elif st.session_state["active_tab"] == 3:
    st.header("📊 数据管理中心")
    
    # 检查是否已登录
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False
    
    # 如果未登录，显示登录界面
    if not st.session_state["admin_logged_in"]:
        st.subheader("🔐 管理员登录")
        
        admin_password = st.text_input("请输入管理员密码", type="password")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔓 登录", type="primary"):
                if verify_admin_password(admin_password):
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
                        success, message = update_admin_password(current_pwd, new_pwd)
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
            stats = get_statistics()
            
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
                
                results = search_questionnaires(
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
                    st.info("💡 CSV导出功能暂未实现，请使用Excel导出")
                    # filename = export_to_csv()
                    # st.success(f"✅ 数据已导出到: {filename}")
                    # 
                    # # 提供下载链接
                    # with open(filename, 'rb') as f:
                    #     st.download_button(
                    #         label="⬇️ 下载 CSV 文件",
                    #         data=f,
                    #         file_name=filename,
                    #         mime='text/csv'
                    #     )
            
            with export_col2:
                if st.button("📊 导出为 Excel"):
                    filename = export_to_excel()
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
            
            all_questionnaires = get_all_questionnaires(limit=100)
            if all_questionnaires:
                df = pd.DataFrame(all_questionnaires)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("暂无问卷数据")
            
            # 数据库信息
            st.subheader("🗄️ 数据库信息")
            st.info("💡 使用 Supabase PostgreSQL 云数据库")
                  
        except Exception as e:
            st.error(f"获取统计数据失败: {e}")
            import traceback
            st.error(traceback.format_exc())
