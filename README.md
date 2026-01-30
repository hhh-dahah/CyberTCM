🧬 CyberTCM 赛博本草 - 启动指南

欢迎来到 CyberTCM 赛博本草 项目！这是一个基于 Python Streamlit 的交互式体质分析应用，结合了赛博朋克视觉风格与传统中医八纲辨证逻辑。

为了确保大家都能顺利运行程序，请严格按照以下步骤配置环境。

🛠️ 第一步：环境准备

1. 安装 Python

确保你的电脑上安装了 Python（建议版本 3.8 或以上）。

打开终端 (Mac) 或 CMD (Windows)，输入以下命令检查：

python --version
# 或者
python3 --version


如果显示版本号，说明已安装。如果报错，请去 Python官网 下载并安装。

2. 获取代码

如果你还没有下载代码，请使用 Git 克隆仓库，或者直接下载 ZIP 压缩包并解压。

git clone <你的GitHub仓库地址>
cd CyberTCM


📦 第二步：安装依赖库

为了不污染你的电脑环境，强烈建议在项目文件夹下打开终端，依次执行以下命令：

1. (可选但推荐) 创建虚拟环境

Windows:

python -m venv venv
.\venv\Scripts\activate


Mac / Linux:

python3 -m venv venv
source venv/bin/activate


激活成功后，你的命令行前面会出现 (venv) 字样。

2. 一键安装所有依赖

确保 requirements.txt 文件在当前目录下，然后运行：

pip install -r requirements.txt


这会自动安装 Streamlit, Pandas, Plotly 等所有需要的库。等待进度条跑完即可。

📂 第三步：检查文件结构

在启动前，请确认你的文件夹里包含以下核心文件：

CyberTCM/
├── app.py                # 主程序入口
├── logic.py              # 核心算法逻辑 (大脑)
├── requirements.txt      # 依赖列表
├── database.xlsx   # 体质数据库 (包含文案、Slogan) 里面两个表单 第一个表单是问题 第二个表单是文案
└── assets/               # [重要] 图片素材文件夹 ##【这个还没画好，先放着】
    ├── CVDQ.png          # 听风者图片
    ├── HSDQ.png          # 破壁者图片
    └── ... (共16张)


注意：如果 assets 文件夹里是空的，或者图片名字不对，程序会自动使用网络头像兜底，不会报错，但效果不如本地图片好。

🚀 第四步：启动程序

看终端结尾
![alt text](image.png)
看终端中文件夹的末尾是否是CyberTCM 
如果不是请输入：
cd CyberTCM进入改文件夹
![alt text](image-1.png)
#然后运行命令

streamlit run app.py


启动成功后：

终端会显示 Local URL: http://localhost:8501。

浏览器会自动弹出一个窗口，显示 CyberTCM 的界面。

如果没有自动弹出，请手动复制 http://localhost:8501 到浏览器打开。

❓ 常见问题 (Q&A)

Q1: 报错 ModuleNotFoundError: No module named 'streamlit'
A: 你忘记安装依赖了！请重新运行 pip install -r requirements.txt。

Q2: 图片显示不出来，或者是随机头像？
A: 请检查 assets 文件夹下是否有对应的图片（例如 CVDQ.png）。图片文件名必须和体质代码完全一致（大写英文）。

Q3: 这里的 Excel/CSV 文件可以修改吗？
A: 可以。修改 database_types.csv 中的文案后，刷新网页即可看到更新。记得保持文件格式（逗号分隔）不变。

Q4: 怎么关闭程序？
A: 在运行程序的终端窗口，按 Ctrl + C 即可停止服务。

Happy Coding! 🧬✨