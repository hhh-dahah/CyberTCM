# CyberTCM 数据管理指南

## 📋 概述

本指南介绍如何查询、管理和导出 CyberTCM 项目收集的数据。我们提供了多种方式来访问和使用您的数据。

## 🗄️ 数据库架构

### 数据库类型
- **SQLite**: 轻量级文件型数据库
- **数据库文件**: `cybertcm.db`（位于项目根目录）

### 数据表结构

#### 1. users（用户表）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 用户ID（主键） |
| nickname | TEXT | 用户昵称 |
| created_at | TIMESTAMP | 创建时间 |

#### 2. questionnaires（问卷表）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 问卷ID（主键） |
| user_id | INTEGER | 用户ID（外键） |
| type_code | TEXT | 体质类型代码 |
| type_name | TEXT | 体质类型名称 |
| radar_data | TEXT | 雷达图数据（JSON格式） |
| energy_data | TEXT | 能量条数据（JSON格式） |
| answers | TEXT | 用户答案（JSON格式） |
| created_at | TIMESTAMP | 提交时间 |

## 🔍 数据查询方法

### 方法1：通过 Streamlit 界面（推荐）

1. **启动应用**
   ```bash
   streamlit run app.py
   ```

2. **访问数据管理页面**
   - 打开浏览器访问 `http://localhost:8501`
   - 点击顶部的 **"📊 数据管理"** 标签页

3. **功能介绍**
   - **📈 数据概览**: 查看总用户数、总问卷数、今日新增
   - **🧬 体质分布**: 查看体质类型分布图表
   - **🔍 数据查询**: 按昵称、体质类型、日期范围搜索
   - **💾 数据导出**: 导出为 CSV 或 Excel 文件
   - **📋 所有记录**: 查看完整的问卷记录列表

### 方法2：使用数据管理工具

1. **运行数据管理脚本**
   ```bash
   python data_manager.py
   ```

2. **功能菜单**
   - `1` - 查看数据统计
   - `2` - 查看所有用户
   - `3` - 查看所有问卷
   - `4` - 搜索问卷
   - `5` - 导出为 CSV
   - `6` - 导出为 Excel
   - `7` - 查看数据库信息
   - `0` - 退出

### 方法3：直接操作数据库

#### 使用 Python
```python
import database

# 获取统计数据
stats = database.get_statistics()
print(f"总用户数: {stats['total_users']}")
print(f"总问卷数: {stats['total_questionnaires']}")

# 获取所有用户
users = database.get_all_users()
for user in users:
    print(f"{user['nickname']}: {user['questionnaire_count']} 份问卷")

# 获取所有问卷
questionnaires = database.get_all_questionnaires()
for q in questionnaires:
    print(f"{q['nickname']} - {q['type_name']}")

# 搜索问卷
results = database.search_questionnaires(
    nickname="张三",
    type_code="CVDQ",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# 导出数据
database.export_to_csv("my_data.csv")
database.export_to_excel("my_data.xlsx")
```

#### 使用 SQLite 命令行
```bash
# 进入 SQLite 命令行
sqlite3 cybertcm.db

# 查看所有表
.tables

# 查看表结构
.schema users
.schema questionnaires

# 查询数据
SELECT * FROM users;
SELECT * FROM questionnaires LIMIT 10;

# 统计查询
SELECT type_name, COUNT(*) as count 
FROM questionnaires 
GROUP BY type_name 
ORDER BY count DESC;

# 退出
.quit
```

#### 使用数据库管理工具
- **DB Browser for SQLite**: 免费图形化工具
- **SQLiteStudio**: 跨平台数据库管理工具
- **DBeaver**: 通用数据库管理工具

## 📤 数据导出

### 导出格式

#### CSV 格式
- 优点：通用性强，可用 Excel 打开
- 包含字段：ID、用户昵称、体质代码、体质名称、雷达数据、提交时间

#### Excel 格式
- 优点：格式美观，支持多工作表
- 包含字段：ID、用户昵称、体质代码、体质名称、雷达数据、能量数据、提交时间

### 导出方法

1. **通过 Streamlit 界面**
   - 进入"📊 数据管理"页面
   - 点击"📄 导出为 CSV"或"📊 导出为 Excel"
   - 点击下载按钮保存文件

2. **通过数据管理工具**
   - 运行 `python data_manager.py`
   - 选择 `5` 导出为 CSV
   - 选择 `6` 导出为 Excel

3. **通过代码**
   ```python
   import database
   database.export_to_csv("export.csv")
   database.export_to_excel("export.xlsx")
   ```

## ☁️ 线上部署数据获取

### Streamlit Cloud 部署

当您将应用部署到 Streamlit Cloud 时，数据获取有以下几种方式：

#### 方式1：通过应用界面导出（推荐）
1. 访问部署后的应用 URL
2. 进入"📊 数据管理"页面
3. 点击导出按钮下载数据
4. 数据文件将下载到您的本地电脑

#### 方式2：数据库文件下载
1. 在 Streamlit Cloud 的管理界面中
2. 找到应用的文件系统
3. 下载 `cybertcm.db` 文件
4. 使用本地 SQLite 工具打开

#### 方式3：定期备份（高级）
```python
# 在应用中添加定期备份功能
import shutil
from datetime import datetime

def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_{timestamp}.db"
    shutil.copy("cybertcm.db", backup_file)
    return backup_file
```

### 数据持久化说明

⚠️ **重要提示**：
- Streamlit Cloud 的免费版本在应用休眠后可能会重置文件系统
- 建议定期导出数据到本地备份
- 对于生产环境，建议使用外部数据库（如 PostgreSQL）

## 📊 数据分析示例

### 体质类型分布分析
```python
import database
import pandas as pd
import matplotlib.pyplot as plt

stats = database.get_statistics()
type_dist = stats['type_distribution']

# 转换为 DataFrame
df = pd.DataFrame(type_dist)

# 绘制饼图
plt.figure(figsize=(10, 6))
plt.pie(df['count'], labels=df['type_name'], autopct='%1.1f%%')
plt.title('体质类型分布')
plt.show()
```

### 用户活跃度分析
```python
import database
from datetime import datetime, timedelta

# 获取最近7天的数据
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

results = database.search_questionnaires(
    start_date=start_date.strftime('%Y-%m-%d'),
    end_date=end_date.strftime('%Y-%m-%d')
)

print(f"最近7天新增问卷: {len(results)} 份")
```

## 🔐 数据安全

### 本地部署
- 数据库文件存储在本地，安全性高
- 建议定期备份数据库文件
- 不要将数据库文件提交到 Git 仓库

### 线上部署
- 使用 HTTPS 协议保护数据传输
- 定期导出数据到安全位置
- 考虑使用环境变量存储敏感信息

## 🛠️ 故障排除

### 常见问题

1. **数据库文件找不到**
   - 检查是否在项目根目录运行
   - 确认 `cybertcm.db` 文件存在

2. **导出失败**
   - 检查是否有写入权限
   - 确认已安装 pandas 和 openpyxl

3. **数据查询为空**
   - 确认已有用户完成问卷
   - 检查数据库连接是否正常

### 联系支持
如有问题，请查看项目文档或提交 Issue。

## 📝 更新日志

- **v1.0**: 初始版本，包含基本的数据管理功能
- **v1.1**: 添加数据导出功能
- **v1.2**: 添加数据查询和统计功能

---

**注意**: 本指南适用于 CyberTCM v0.1 及以上版本。
