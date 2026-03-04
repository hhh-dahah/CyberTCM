# Supabase 数据库迁移指南

本指南将帮助你将 CyberTCM 项目从 SQLite 迁移到 Supabase。

---

## 第一步：创建 Supabase 项目

1. 访问 [supabase.com](https://supabase.com) 并注册/登录
2. 点击 "New Project" 创建新项目
3. 填写项目信息：
   - Name: `CyberTCM`
   - Database Password: 设置一个强密码（请妥善保存）
   - Region: 选择离你最近的区域（推荐选择新加坡或东京）
4. 等待项目创建完成（约 2 分钟）

---

## 第二步：获取连接信息

项目创建完成后：

1. 进入项目 Dashboard
2. 点击左侧菜单 **Settings** → **API**
3. 复制以下信息：
   - **Project URL**: `https://xxxxxx.supabase.co`
   - **anon public**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

---

## 第三步：创建数据库表

### 方法一：使用 SQL Editor（推荐）

1. 在 Supabase Dashboard 左侧菜单点击 **SQL Editor**
2. 点击 **New query**
3. 复制以下 SQL 并执行：

```sql
-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    nickname TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建管理员密码表
CREATE TABLE IF NOT EXISTS admin_password (
    id SERIAL PRIMARY KEY,
    password TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建完整问卷表
CREATE TABLE IF NOT EXISTS complete_questionnaires (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    -- 八纲辨证结果
    bagang_type_code TEXT,
    bagang_type_name TEXT,
    bagang_radar_data TEXT,
    bagang_energy_data TEXT,
    bagang_answers TEXT,
    -- 卫健委结果
    wjw_main_constitution TEXT,
    wjw_main_score INTEGER,
    wjw_main_result TEXT,
    wjw_all_results TEXT,
    wjw_scores TEXT,
    wjw_answers TEXT,
    -- 原始答案
    raw_answers TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_nickname ON users(nickname);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_complete_user_id ON complete_questionnaires(user_id);
CREATE INDEX IF NOT EXISTS idx_complete_bagang_type ON complete_questionnaires(bagang_type_code);
CREATE INDEX IF NOT EXISTS idx_complete_wjw_main ON complete_questionnaires(wjw_main_constitution);
CREATE INDEX IF NOT EXISTS idx_complete_created_at ON complete_questionnaires(created_at);

-- 插入默认管理员密码
INSERT INTO admin_password (password) VALUES ('8888')
ON CONFLICT DO NOTHING;
```

### 方法二：使用旧版表结构（如果需要）

```sql
-- 创建旧版问卷表（可选）
CREATE TABLE IF NOT EXISTS questionnaires (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    type_code TEXT NOT NULL,
    type_name TEXT NOT NULL,
    radar_data TEXT NOT NULL,
    energy_data TEXT NOT NULL,
    answers TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建旧版问卷表索引
CREATE INDEX IF NOT EXISTS idx_questionnaires_user_id ON questionnaires(user_id);
CREATE INDEX IF NOT EXISTS idx_questionnaires_type_code ON questionnaires(type_code);
CREATE INDEX IF NOT EXISTS idx_questionnaires_created_at ON questionnaires(created_at);
```

---

## 第四步：配置项目

### 1. 安装依赖

```bash
pip install supabase python-dotenv
```

### 2. 创建 .env 文件

在项目根目录创建 `.env` 文件：

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key
```

### 3. 在 app.py 中切换数据库

修改 `app.py` 顶部的导入语句：

```python
# 注释掉旧的 SQLite 导入
# from database import (
#     init_db, get_or_create_user, save_complete_questionnaire,
#     verify_admin_password, update_admin_password,
#     get_statistics, search_questionnaires, export_to_excel
# )

# 使用新的 Supabase 导入
from database_supabase import (
    init_db, get_or_create_user, save_complete_questionnaire,
    verify_admin_password, update_admin_password,
    get_statistics, search_questionnaires, export_to_excel
)
```

---

## 第五步：迁移现有数据（可选）

如果你有现有 SQLite 数据需要迁移：

```bash
python data_manager.py
```

然后选择导出选项，将数据导出为 Excel，再手动导入到 Supabase。

---

## 安全提示

⚠️ **重要安全提醒：**

1. **永远不要将 `.env` 文件提交到 Git**（已在 `.gitignore` 中配置）
2. 定期更换 Supabase 数据库密码
3. 在生产环境中使用 Service Role Key 替代 anon key（需要修改 Row Level Security）
4. 建议启用 Supabase 的 Row Level Security (RLS)

---

## 故障排除

### 问题：连接失败
- 检查 `.env` 文件中的 URL 和 Key 是否正确
- 确保 Supabase 项目已完全启动

### 问题：权限错误
- 检查 Supabase Dashboard 中的 Table Editor → 表权限
- 确保 anon 角色有 INSERT/SELECT 权限

### 问题：时区问题
- Supabase 使用 UTC 时区，应用会自动处理
