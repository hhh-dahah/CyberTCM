# Streamlit Cloud 数据库连接配置指南

## ⚠️ 问题诊断

### 为什么之前的配置不生效？

1. **`load_dotenv()` 在 Streamlit Cloud 上无效**
   - Streamlit Cloud 不使用 `.env` 文件
   - Streamlit Cloud 使用 **Secrets** 机制管理敏感信息

2. **代码使用 `os.getenv()` 读取环境变量**
   - Streamlit Cloud 的 Secrets 需要通过 `st.secrets[]` 访问
   - 直接写死密码也不生效是因为代码在模块加载时就尝试读取配置

---

## ✅ 解决方案（已完成）

### 1. 代码层面修改

已修改 `database_postgres.py`，现在支持：
- ✅ Streamlit Cloud Secrets（云端部署）
- ✅ 环境变量（本地开发）
- ✅ 自动检测环境并切换

### 2. Streamlit Cloud 配置步骤

#### 步骤 1：打开 Secrets 管理界面
1. 访问 https://share.streamlit.io
2. 找到你的应用
3. 点击 **"Settings"** → **"Secrets"**

#### 步骤 2：添加 Secrets
将以下内容复制到 Secrets 编辑框：

```toml
DB_USER = "postgres.xlxrkhyontvupqdlmfdf"
DB_PASSWORD = "RaX6lCmRbcV3o8uo"
DB_HOST = "aws-1-ap-northeast-1.pooler.supabase.com"
DB_PORT = "5432"
DB_NAME = "postgres"
```

#### 步骤 3：保存并重新部署
1. 点击 **"Save"**
2. 应用会自动重新部署
3. 等待约 1-2 分钟

---

## 🔍 验证方法

### 方法 1：查看日志
1. 在 Streamlit Cloud 应用页面，点击右上角 **"⚙️"**
2. 选择 **"View app logs"**
3. 检查是否有数据库连接错误

### 方法 2：添加调试代码（临时）
在 `app.py` 中添加：

```python
import streamlit as st

# 检查配置是否加载成功
try:
    import streamlit as st
    if hasattr(st, 'secrets') and 'DB_HOST' in st.secrets:
        st.success("✅ 成功从 Secrets 读取配置")
        st.info(f"DB_HOST: {st.secrets['DB_HOST']}")
except:
    st.warning("⚠️ 未检测到 Secrets 配置")
```

---

## 🛠️ 本地测试

### 方式 1：使用 .env 文件（推荐）
保持现有的 `.env` 文件配置，代码会自动检测。

### 方式 2：使用本地 Secrets
创建 `.streamlit/secrets.toml`（已在 `.gitignore` 中排除）：

```toml
DB_USER = "postgres.xlxrkhyontvupqdlmfdf"
DB_PASSWORD = "RaX6lCmRbcV3o8uo"
DB_HOST = "aws-1-ap-northeast-1.pooler.supabase.com"
DB_PORT = "5432"
DB_NAME = "postgres"
```

---

## 📝 文件清单

| 文件 | 用途 | 是否提交 |
|------|------|---------|
| `database_postgres.py` | 数据库连接逻辑（已更新） | ✅ 是 |
| `.streamlit/secrets.toml` | Streamlit Cloud Secrets 配置示例 | ❌ 否（在 .gitignore 中） |
| `.streamlit/secrets_local.toml` | 本地测试配置 | ❌ 否（在 .gitignore 中） |
| `.env.example` | 环境变量示例 | ✅ 是 |
| `.gitignore` | Git 忽略配置（已更新） | ✅ 是 |

---

## ⚡ 快速部署检查清单

- [ ] 修改 `database_postgres.py` 已提交
- [ ] 在 Streamlit Cloud Secrets 中添加配置
- [ ] 等待自动重新部署完成
- [ ] 查看日志确认无错误
- [ ] 测试网站功能是否正常

---

## 🚨 常见错误排查

### 错误 1：`psycopg2.OperationalError: connection refused`
**原因**：数据库配置错误或 Supabase 未允许外部连接

**解决**：
1. 检查 Secrets 配置是否正确
2. 在 Supabase Dashboard → Settings → Database → Connection pooling
3. 确保启用外部连接

### 错误 2：`KeyError: 'DB_HOST'`
**原因**：Secrets 未配置或配置名称错误

**解决**：
1. 检查 Secrets 中是否包含所有 5 个配置项
2. 确认配置名称完全一致（区分大小写）

### 错误 3：配置修改后仍不生效
**原因**：Streamlit Cloud 缓存

**解决**：
1. 在 Streamlit Cloud 点击 **"Restart"**
2. 或推送一个空提交触发重新部署：
   ```bash
   git commit --allow-empty -m "Trigger redeploy"
   git push origin master
   ```

---

## 📞 需要帮助？

如果仍有问题，请提供：
1. Streamlit Cloud 的错误日志截图
2. 确认 Secrets 配置已保存
3. 本地运行是否正常
