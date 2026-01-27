import streamlit as st

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

# --- 模块 1: 问卷区 ---
with tab1:
    st.header("第一阶段: 基础数据采集")
    
    # 布局：把问题分成两列，好看一点
    col1, col2 = st.columns(2)
    
    with col1:
        q1 = st.radio("1. 你冬天是否手脚冰凉?", ["A. 经常", "B. 偶尔", "C. 从不"])
        q2 = st.radio("2. 你容易口腔溃疡吗?", ["A. 经常", "B. 偶尔", "C. 从不"])
    
    with col2:
        q3 = st.radio("3. 你是否容易疲劳?", ["A. 葛优躺", "B. 还可以", "C. 精神小伙"])
        q4 = st.radio("4. 脸上容易出油吗?", ["A. 大油田", "B. T区油", "C. 干爽"])

    if st.button("提交数据 (Upload)"):
        st.toast("数据上传成功！正在计算...", icon="🚀")

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
    st.empty() # 占位符，以后放雷达图
    st.info("👈 请先完成左侧测试")