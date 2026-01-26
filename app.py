import streamlit as st
import time

# 1. 设置网页标题和图标
st.set_page_config(page_title="赛博本草 MVP", page_icon="💊")

# 2. 也是赛博风格的标题
st.title("TCM-BTI: 航天鼠鼠队辨识系统")
st.markdown("### 拒绝病历本，做 Z 世代的身体说明书")

# 3. 搞个侧边栏
with st.sidebar:
    st.header("功能控制台")
    st.write("当前版本: v0.1 Alpha")
    # 一个滑块
    confidence = st.slider("算法置信度阈值", 0, 100, 80)

# 4. 模拟一个交互按钮
col1, col2 = st.columns(2) # 把屏幕分成两列

with col1:
    st.info("请点击下方按钮启动神经连接...")
    if st.button("启动检测 (Start Scan)"):
        # 模拟进度条
        progress_text = "正在接入生物电信号..."
        my_bar = st.progress(0, text=progress_text)

        for percent_complete in range(100):
            time.sleep(0.01) # 假装在计算
            my_bar.progress(percent_complete + 1, text=progress_text)
        
        st.success("连接成功！体质数据已同步。")
        st.balloons() # 放个气球庆祝一下

with col2:
    # 显示一张图片 (这里先用网络图片代替，以后换成你们的舌象图)
    st.image("https://streamlit.io/images/brand/streamlit-mark-color.png", caption="系统核心运行中")

# 5. 显示一些调试信息
st.write("---")
st.write(f"当前设定的阈值是: {confidence}%")