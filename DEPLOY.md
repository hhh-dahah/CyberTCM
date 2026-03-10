# 服务器部署指南

本文档帮助你将 CyberTCM 项目部署到服务器（如 Railway、Render、Vercel 等）。

---

## 本地准备

### 1. 确保 .env 文件配置正确

```env
# Supabase 配置
SUPABASE_URL=https://xlxrkhyontvupqdlmfdf.supabase.co
SUPABASE_KEY=your-anon-public-key

# PostgreSQL 直接连接配置
DB_USER=postgres.xlxrkhyontvupqdlmfdf
DB_PASSWORD=RaX6lCmRbcV3o8uo
DB_HOST=aws-1-ap-northeast-1.pooler.supabase.com
DB_PORT=5432
DB_NAME=postgres
```

### 2. 提交代码到 GitHub

确保以下文件已提交：
- `app.py`
- `database_postgres.py`
- `requirements.txt`
- `.streamlit/config.toml`

---

## 服务器部署步骤

### 方式一：使用 Railway（推荐）

1. **注册 Railway**
   - 访问 https://railway.app
   - 使用 GitHub 登录

2. **创建项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你的仓库

3. **添加环境变量**
   - 在 Railway Dashboard 中，点击项目
   - 点击 "Variables" tab
   - 添加以下变量：
     ```
     DB_USER=postgres.xlxrkhyontvupqdlmfdf
     DB_PASSWORD=RaX6lCmRbcV3o8uo
     DB_HOST=aws-1-ap-northeast-1.pooler.supabase.com
     DB_PORT=5432
     DB_NAME=postgres
     ```

4. **部署**
   - Railway 会自动安装依赖并部署

### 方式二：使用 Render

1. **注册 Render**
   - 访问 https://render.com
   - 使用 GitHub 登录

2. **创建 Web Service**
   - 点击 "New Web Service"
   - 选择你的仓库
   - 设置：
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `streamlit run app.py --server.port=$PORT`

3. **添加环境变量**
   - 同 Railway，在 Environment Variables 中添加

### 方式三：使用自己的服务器（VPS）

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **创建 .env 文件**
   ```bash
   nano .env
   # 粘贴环境变量内容
   ```

3. **使用 tmux 或 screen 运行**
   ```bash
   tmux new -s cybertcm
   streamlit run app.py --server.port=8501
   # 按 Ctrl+B 然后按 D 退出 tmux
   ```

4. **使用 nginx 反向代理**（可选）
   - 配置 nginx 将域名指向 Streamlit 端口

---

## 常见问题

### 问题1：页面空白/无法访问

**原因**：环境变量未配置

**解决方法**：
1. 检查服务器上的环境变量是否正确
2. 查看应用日志：`streamlit run app.py`

### 问题2：数据库连接失败

**原因**：数据库连接信息错误

**解决方法**：
1. 确认 .env 文件中的数据库连接信息正确
2. 检查 Supabase 的数据库是否允许外部连接

### 问题3：依赖安装失败

**原因**：网络问题或 Python 版本不匹配

**解决方法**：
```bash
# 指定 Python 版本
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 注意事项

⚠️ **安全提醒**：
1. **不要将 .env 文件提交到 GitHub**（已在 .gitignore 中排除）
2. **定期更换数据库密码**
3. **使用强密码**

---

## 本地测试服务器配置

在本地测试部署配置：
```bash
# 模拟服务器环境
export DB_USER=postgres.xlxrkhyontvupqdlmfdf
export DB_PASSWORD=RaX6lCmRbcV3o8uo
export DB_HOST=aws-1-ap-northeast-1.pooler.supabase.com
export DB_PORT=5432
export DB_NAME=postgres

streamlit run app.py
```
