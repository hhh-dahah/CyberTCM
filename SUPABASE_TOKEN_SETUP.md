# Supabase Token 获取指南

本指南将帮助你注册 Supabase 账号并获取所需的 token（API Key）。

---

## 第一步：注册 Supabase 账号

1. **访问 Supabase 官网**：[https://supabase.com](https://supabase.com)

2. **点击 "Start your project" 或 "Sign Up"**

3. **选择注册方式**：
   - 使用 GitHub 账号（推荐，最快捷）
   - 使用 Google 账号
   - 使用电子邮件注册

4. **完成注册流程**
   - 如果使用邮件注册，需要验证邮箱
   - 设置密码（请使用强密码）

---

## 第二步：创建 Supabase 项目

1. **登录后**，在 Supabase Dashboard 点击 **"New Project"**

2. **填写项目信息**：
   - **Project Name**: `CyberTCM`
   - **Database Password**: 设置一个强密码（请妥善保存）
   - **Region**: 选择离你最近的区域（推荐：Singapore 或 Tokyo）

3. **点击 "Create project"**
   - 等待项目创建完成（约 2 分钟）

---

## 第三步：获取 API Key (Token)

项目创建完成后：

1. 在左侧菜单点击 **"Settings"** → **"API"**

2. 在 **"Project API keys"** 部分，找到：
   - **Project URL**: `https://xxxxxx.supabase.co`
   xlxrkhyontvupqdlmfdf
   https://xlxrkhyontvupqdlmfdf.supabase.co
   - **anon public**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   sb_publishable_ifSoRb-G0y_bSU65-Fjw3w_7Q03EOfK

3. **复制这两个值**
   - Project URL = SUPABASE_URL
   - anon public = SUPABASE_KEY（这就是我们需要的 token）

---

## 第四步：配置 .env 文件

1. **创建 .env 文件**：
   ```bash
   cp .env.example .env
   ```

2. **编辑 .env 文件**，填入你的 Supabase 信息：
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-anon-public-key
   ```

3. **保存文件**

---

## 第五步：切换到 Supabase 数据库

修改 `app.py` 文件顶部的导入语句：

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

## 第六步：重启应用

```bash
# 先停止之前的 Streamlit 服务（如果运行中）
# 然后重新启动
streamlit run app.py
```

---

## 验证连接

应用启动后：
- 打开浏览器访问应用
- 尝试提交一份问卷
- 检查 Supabase Dashboard 中的 **Table Editor**，确认数据是否正确存储

---

## 故障排除

### 问题：连接失败
- 检查 .env 文件中的 URL 和 Key 是否正确
- 确保没有多余的空格或换行
- 验证 Supabase 项目是否完全启动

### 问题：权限错误
- 在 Supabase Dashboard 中，点击 **Table Editor**
- 选择相应的表，点击 **"Edit"** → **"Permissions"**
- 确保 **anon** 角色有 **INSERT** 和 **SELECT** 权限

### 问题：导入错误
- 确保已安装依赖：`pip install -r requirements.txt`

---

## 安全提示

⚠️ **重要**：
- 永远不要将 `.env` 文件提交到 Git（已在 `.gitignore` 中配置）
- 定期更换 Supabase 数据库密码
- 在生产环境中，建议使用 Service Role Key 并启用 Row Level Security
