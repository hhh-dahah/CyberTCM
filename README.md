# 🧬 CyberTCM 赛博本草

> 你的专属体质说明书 —— 基于中医理论的智能体质评估系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.24+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📖 项目简介

**CyberTCM（赛博本草）** 是一个基于 Streamlit 开发的中医体质评估 Web 应用。通过科学的问卷评估体系，帮助用户了解自己的体质类型，并提供个性化的健康调理建议。

### ✨ 核心特性

- 🧬 **双维度体质评估**：融合传统八纲辨证与现代卫健委9种体质标准
- 📊 **可视化报告**：雷达图、能量条直观展示体质偏颇
- 💾 **数据持久化**：SQLite 数据库存储，支持历史记录查询
- 🔐 **管理员后台**：密码保护的数据管理中心
- 📤 **数据导出**：支持 CSV、Excel 格式导出
- 📱 **响应式设计**：适配桌面和移动设备

---

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- pip 包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd CyberTCM
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动应用**
```bash
streamlit run app.py
```

4. **访问应用**
打开浏览器访问 `http://localhost:8501`

---

## 📋 问卷说明

本系统包含 **61道题目**，预计完成时间 **5-8分钟**：

| 问卷部分 | 题目数量 | 评估维度 |
|---------|---------|---------|
| PBTI体质（八纲辨证） | 28题 | 寒热、虚实、燥湿、郁瘀 |
| 卫健委体质 | 33题 | 气虚、阳虚、阴虚、痰湿、湿热、血瘀、气郁、特禀、平和 |

> 💡 **温馨提示**：问卷默认选项为"一般"，请根据实际情况选择最符合的选项

---

## 🏗️ 项目架构

```
CyberTCM/
├── app.py                 # Streamlit 主应用入口
├── logic.py               # 体质计算核心逻辑
├── database.py            # SQLite 数据库操作
├── data_manager.py        # 命令行数据管理工具
├── database.xlsx          # 八纲辨证题库
├── database1.xlsx         # 卫健委题库
├── cybertcm.db            # SQLite 数据库文件
├── requirements.txt       # Python 依赖
├── DATA_GUIDE.md          # 数据管理指南
└── .streamlit/
    └── config.toml        # Streamlit 配置
```

### 核心模块

| 文件 | 功能说明 |
|------|---------|
| `app.py` | Streamlit 前端界面，包含问卷、报告、数据管理三大模块 |
| `logic.py` | 体质计算算法，包含八纲辨证和卫健委两种评估体系 |
| `database.py` | 数据库连接池、CRUD 操作、数据导出功能 |
| `data_manager.py` | 命令行数据管理工具 |

---

## 🧪 体质评估体系

### 八纲辨证（PBTI体质）

基于中医八纲理论，从四个维度评估体质：

| 维度 | 对立面 | 说明 |
|------|-------|------|
| 温度 | 寒 ↔ 热 | 身体寒热倾向 |
| 能量 | 虚 ↔ 实 | 正气盛衰状态 |
| 环境 | 燥 ↔ 湿 | 体内津液分布 |
| 通畅 | 郁 ↔ 瘀 | 气血运行状况 |

**体质代码生成规则**：
- 第1位：C(寒) / H(热)
- 第2位：V(虚) / S(实)
- 第3位：D(燥) / W(湿)
- 第4位：Q(郁) / B(瘀)

**特殊体质**：当四个维度得分均较低时，判定为 **SSR（天选之子/平和质）**

### 卫健委9种体质

依据国家卫健委《中医体质分类与判定》标准：

| 体质类型 | 判定标准 |
|---------|---------|
| 气虚质 | ≥11分：是 / 9-10分：倾向是 / ≤8分：否 |
| 阳虚质 | 同上 |
| 阴虚质 | 同上 |
| 痰湿质 | 同上 |
| 湿热质 | 同上 |
| 血瘀质 | 同上 |
| 气郁质 | 同上 |
| 特禀质 | 同上 |
| 平和质 | ≥17分且其他8种≤8分：是 / ≥17分且其他8种≤10分：基本是 |

---

## 📊 数据管理

### 管理员功能

1. 点击顶部 **"📊 数据管理"** 标签
2. 输入管理员密码（默认：`8888`）
3. 登录后可使用以下功能：
   - 📈 查看数据统计（用户数、问卷数、体质分布）
   - 🔍 按昵称、体质类型、日期搜索
   - 💾 导出 CSV / Excel 文件
   - 🔧 修改管理员密码

### 命令行工具

```bash
python data_manager.py
```

功能菜单：
- `1` - 查看数据统计
- `2` - 查看所有用户
- `3` - 查看所有问卷
- `4` - 搜索问卷
- `5` - 导出为 CSV
- `6` - 导出为 Excel
- `7` - 查看数据库信息
- `0` - 退出

详细说明请参考 [DATA_GUIDE.md](DATA_GUIDE.md)

---

## 🗄️ 数据库结构

### 数据表

**users（用户表）**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 用户ID（主键） |
| nickname | TEXT | 用户昵称 |
| created_at | TIMESTAMP | 创建时间 |

**complete_questionnaires（完整问卷表）**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 问卷ID（主键） |
| user_id | INTEGER | 用户ID（外键） |
| bagang_type_code | TEXT | 八纲体质代码 |
| bagang_type_name | TEXT | 八纲体质名称 |
| wjw_main_constitution | TEXT | 卫健委主要体质 |
| wjw_main_score | INTEGER | 主要体质得分 |
| raw_answers | TEXT | 原始答案（JSON） |
| created_at | TIMESTAMP | 提交时间 |

---

## 🛠️ 技术栈

- **前端框架**: [Streamlit](https://streamlit.io/) - Python 数据应用框架
- **数据可视化**: [Plotly](https://plotly.com/) - 交互式图表
- **数据处理**: [Pandas](https://pandas.pydata.org/) - 数据分析
- **数据库**: [SQLite](https://sqlite.org/) - 轻量级文件数据库
- **样式**: 自定义 CSS + Streamlit 原生组件

---

## 📝 更新日志

### v1.0 Alpha
- ✅ 双维度体质评估（八纲辨证 + 卫健委）
- ✅ 可视化报告（雷达图、能量条）
- ✅ 数据持久化存储
- ✅ 管理员后台
- ✅ 数据导出功能
- 🚧 舌象识别（开发中）

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建你的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源协议。

---

## 🙏 致谢

- 感谢国家卫健委发布的《中医体质分类与判定》标准
- 感谢 Streamlit 团队提供的优秀框架
- 感谢所有测试用户的反馈和建议

---

<div align="center">

**Made with ❤️ and 🐍 Python**

</div>
