import streamlit as st
import logic # 引入我们的大脑

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

/* 4. 卡片容器：黑钻质感 */
div[data-testid="stVerticalBlock"] > div {
    background-color: rgba(255, 255, 255, 0.03); /* 极淡的白透明 */
    border: 1px solid rgba(0, 255, 200, 0.2); 
    border-radius: 12px;
    padding: 20px;
    backdrop-filter: blur(5px);
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
# 2. 侧边栏：控制中心
with st.sidebar:
    st.title("🔋 能量控制台")
    st.info("系统版本: v0.1 Alpha")
    
    # 模拟登录
    user_name = st.text_input("输入代号 (ID):", "Player1")
    st.write(f"欢迎回来, {user_name}")
    
    st.divider() # 分割线
    st.write("🔧 调试工具")
    if st.button("清除缓存 (Reset)"):
        st.cache_data.clear()
        st.success("内存已释放")

# 3. 主界面：赛博标题
st.title("👾 TCM-BTI：你的赛博体质说明书")
st.markdown("##### *✨ 科学解码 · 国潮养生 · 寻找你的体质同类*")

# 4. 核心功能区 (用 Tabs 分页)
tab1, tab2, tab3 = st.tabs(["🧬 快速扫描 (问卷)", "📸 舌象解码 (AI)", "🔮 专属体质报告"])

# --- 模块 1: 问卷区 (动态版) ---
with tab1:
    st.header("🧬 第一阶段: 基础数据采集")
    
    # 1. 调用大脑，加载题目
    df_questions = logic.load_questions()
    
    # 2. 创建一个表单 (Form)，这样用户填完所有题点提交才会刷新
    with st.form("quiz_form"):
        # 遍历题库，自动生成题目
        for index, row in df_questions.iterrows():
            st.write(f"**{row['question']}**")
            # 这里的 key 是关键，用来区分每一道题
            st.radio(
                "请选择程度:", 
                ["A. 非常符合 (5分)", "B. 比较符合 (4分)", "C. 一般 (3分)", "D. 不太符合 (2分)", "E. 完全不符 (1分)"],
                key=f"q_{row['id']}", # 给每个题目一个唯一的身份证号
                index=2, # 默认选 C
                horizontal=True, # 选项横着排
                label_visibility="collapsed" # 隐藏多余的标签
            )
            st.markdown("---") # 分割线

        # 3. 提交按钮
        submitted = st.form_submit_button("🚀 生成体质报告", type="primary")
        
        if submitted:
            # 调用算分函数
            result_scores = logic.calculate_score(st.session_state, df_questions)
            
            # 存入 Session，这样切换 Tab 数据不会丢
            st.session_state["quiz_result"] = result_scores
            
            st.success("✅ 数据解算完成！请点击顶部的 [专属体质报告] 查看结果。")
            st.balloons()

# --- 模块 2: 视觉区 ---
with tab2:
    st.header("第二阶段: 生物特征识别")
    st.warning("⚠️ 请在光线充足环境下拍摄舌象")
    
    # 上传组件
    uploaded_file = st.file_uploader("上传舌头照片", type=['jpg', 'png'])
    if uploaded_file:
        st.image(uploaded_file, caption="样本采集成功", width=300)

# --- 模块 3: 结果区 ---
with tab3:
    if "quiz_result" in st.session_state:
        st.subheader("📊 您的赛博体质雷达")
        
        # 获取分数
        scores = st.session_state["quiz_result"]
        
        # 找出得分最高的体质 (简单版判断)
        max_type = max(scores, key=scores.get)
        max_score = scores[max_type]
        
        st.metric(label="主导判定", value=f"{max_type}质", delta=f"得分: {max_score}")
        
        # 显示所有分数 (临时)
        st.json(scores)
        
        st.info("💡 提示：更详细的雷达图和调理方案正在开发中...")
        
    else:
        st.warning("⚠️ 暂无数据，请先去 [Tab 1] 完成问卷提交。")