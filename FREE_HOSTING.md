# 免费 Streamlit 部署指南

以下是最流行的免费 Streamlit 托管方案：

---

## 方案一：Streamlit Community Cloud（推荐）

**免费**：✅ 完全免费
**特点**：Streamlit 官方托管，专为 Streamlit 设计

### 部署步骤：

1. **准备代码**
   - 确保代码已推送到 GitHub 公开仓库
   - 创建 `.streamlit/config.toml` 文件

2. **创建 config.toml**
   ```toml
   [server]
   port = 8501
   headless = true
   enableCORS = false
   enableXsrfProtection = true

   [theme]
   primaryColor = "#00CBA0"
   ```

3. **部署**
   - 访问 https://share.streamlit.io
   - 使用 GitHub 登录
   - 选择你的 GitHub 仓库
   - 设置：
     - Branch: `main`
     - Main file path: `app.py`
   - 点击 "Deploy"

---

## 方案二：Hugging Face Spaces

**免费**：✅ 完全免费
**特点**：支持 Streamlit 和 Gradio，功能强大

### 部署步骤：

1. **准备代码**
   - 确保代码已推送到 GitHub

2. **创建 Hugging Face Space**
   - 访问 https://huggingface.co/spaces
   - 点击 "Create new Space"
   - 填写：
     - Space name: `cybertcm`
     - License: `MIT`
     - Visibility: `Public`
     - SDK: `Streamlit`

3. **部署方式**

   **方式A：直接从 GitHub 部署**
   - 在 Space 设置中选择 "Link to GitHub repository"
   - 选择你的仓库

   **方式B：手动上传**
   - 在本地创建 `app.py` 和 requirements.txt
   - 手动拖拽到 Hugging Face

4. **配置环境变量**
   - 在 Space 设置中添加 Variables：
     ```
     DB_USER=postgres.xlxrkhyontvupqdlmfdf
     DB_PASSWORD=RaX6lCmRbcV3o8uo
     DB_HOST=aws-1-ap-northeast-1.pooler.supabase.com
     DB_PORT=5432
     DB_NAME=postgres
     ```

---

## 方案三：Render 免费版

**免费**：✅ 有免费额度
**特点**：支持多种技术栈

### 部署步骤：

1. **注册**
   - 访问 https://render.com
   - 使用 GitHub 登录

2. **创建 Web Service**
   - 点击 "New Web Service"
   - 连接到你的 GitHub 仓库

3. **配置**
   - Name: `cybertcm`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

4. **添加环境变量**
   - 在 Environment 中添加数据库连接信息

---

## 对比

| 方案 | 免费 | 私有部署 | 自动部署 | 推荐指数 |
|------|------|----------|----------|----------|
| Streamlit Cloud | ✅ | ❌ | ✅ | ⭐⭐⭐⭐⭐ |
| Hugging Face | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| Render | ✅ | ✅ | ✅ | ⭐⭐⭐ |

---

## 重要提醒

⚠️ **数据库连接问题**：

由于你的项目使用 Supabase PostgreSQL，直接连接可能会遇到问题。有两种解决方案：

### 方案A：使用 Supabase API（推荐）
- 使用 `database_supabase.py` 而不是 `database_postgres.py`
- 不需要直接连接 PostgreSQL

### 方案B：配置 Supabase 允许外部连接
- 在 Supabase Dashboard → Settings → Database
- 找到 "Connection pooling"
- 启用外部连接

---

## 推荐选择

**如果你的项目是公开的**：使用 **Streamlit Community Cloud**
- 完全免费
- 部署简单
- 自动从 GitHub 部署

**如果需要私有部署**：使用 **Hugging Face Spaces**
- 免费且支持私有
- 可以添加环境变量
