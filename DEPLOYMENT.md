# 部署指南

本文档详细说明如何将任务管理系统部署到生产环境。

## 🚀 部署选项

### 选项1：完全免费部署（推荐）

- **后端**：Render（免费版）
- **前端**：GitHub Pages（免费）
- **数据库**：SQLite（本地存储）
- **通知**：Telegram Bot（免费）

**总成本**：$0/月

### 选项2：使用自有服务器

- **后端**：你的VPS/云服务器
- **前端**：Nginx
- **数据库**：SQLite或PostgreSQL
- **通知**：Telegram Bot

**总成本**：服务器费用（取决于你的配置）

---

## 📋 部署前准备

### 1. GitHub账号

- 注册GitHub账号（免费）
- Fork本项目到你的账号

### 2. Telegram Bot配置

#### 获取Bot Token

1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称
4. 获取Bot Token（类似：`1234567890:ABCdefGHIjkLmnoPQRstuVWxyz`）

#### 获取Chat ID

1. 在Telegram中搜索 `@userinfobot`
2. 发送任意消息
3. 获取你的Chat ID（类似：`123456789`）

#### 测试Bot

1. 在Telegram中搜索你的Bot（通过用户名）
2. 发送 `/start`
3. 回复一条消息

### 3. Render账号

1. 访问 https://render.com
2. 使用GitHub账号登录
3. 验证邮箱（免费账户需要）

---

## 🔧 部署到Render（后端）

### 步骤1：创建Web Service

1. 登录Render Dashboard
2. 点击 "New +" → "Web Service"
3. 选择Fork后的仓库
4. 配置构建和启动

### 步骤2：配置构建设置

**Name**: `todo-system-backend`

**Environment**: `Python 3`

**Build Command**:
```bash
cd backend && pip install -r requirements.txt
```

**Start Command**:
```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 10000
```

### 步骤3：配置环境变量

在Render Dashboard的Environment选项卡中添加：

```bash
APP_NAME=Todo System
VERSION=1.0.0
DEBUG=False
DATABASE_PATH=database/todo.db
TELEGRAM_BOT_TOKEN=你的Bot Token
TELEGRAM_CHAT_ID=你的Chat ID
```

### 步骤4：部署

点击 "Create Web Service"，等待部署完成（约2-3分钟）。

部署成功后，你会得到一个URL（类似：`https://todo-system-backend.onrender.com`）。

### 步骤5：获取Deploy Hook

1. 在Render Service页面
2. 找到 "Deploys" 选项卡
3. 点击 "Add Deploy Hook"
4. 复制Webhook URL（类似：`https://api.render.com/deploy/srv-xxx/xxx`）

---

## 🌐 部署到GitHub Pages（前端）

### 步骤1：启用GitHub Pages

1. 进入Fork后的仓库
2. 点击 "Settings" → "Pages"
3. 在 "Source" 下选择 `Deploy from a branch`
4. 选择 `main` 分支，`/ (root)` 目录
5. 点击 "Save"

### 步骤2：修改前端API配置

编辑 `frontend/js/app.js`，修改API_BASE_URL：

```javascript
const API_BASE_URL = 'https://todo-system-backend.onrender.com/api';
```

### 步骤3：提交更改

```bash
git add frontend/js/app.js
git commit -m "Update API URL for production"
git push origin main
```

GitHub Pages会自动部署前端（约1-2分钟）。

### 步骤4：访问前端

访问：`https://your-username.github.io/todo-system/`

---

## 🔗 连接前后端

### 步骤1：配置CORS

确保后端的FastAPI配置允许前端域名访问。

在 `backend/app/main.py` 中，CORS已配置为允许所有域名（`allow_origins=["*"]`）。

**生产环境建议**：修改为只允许前端域名：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-username.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 步骤2：测试连接

1. 访问前端页面
2. 点击 "筛选" 或添加任务
3. 检查浏览器控制台是否有错误
4. 检查Network标签，确认API请求成功

---

## 🔄 自动部署（CI/CD）

### 配置GitHub Actions

本项目的GitHub Actions工作流（`.github/workflows/ci-cd.yml`）已经配置好：

1. **推送代码时**：
   - 运行测试
   - 代码质量检查
   - 如果通过，自动部署前端到GitHub Pages

2. **合并PR时**：
   - 运行所有测试
   - 代码审查
   - 自动部署后端和前端

### 触发后端自动部署（可选）

如果你希望推送代码时自动触发Render部署：

1. 在GitHub仓库中添加Secret：
   - 进入 "Settings" → "Secrets and variables" → "Actions"
   - 添加 `RENDER_DEPLOY_HOOK`，值为Render的Deploy Hook URL

2. 修改 `.github/workflows/ci-cd.yml`，取消注释相关代码

---

## 📊 监控和日志

### Render日志

1. 在Render Dashboard选择你的Service
2. 点击 "Logs" 选项卡
3. 查看实时日志和错误信息

### GitHub Actions日志

1. 在GitHub仓库中点击 "Actions"
2. 选择workflow运行记录
3. 查看详细的构建和部署日志

---

## 🔒 安全配置

### 1. 保护敏感信息

**不要**提交以下文件到Git：
- `backend/.env`（使用 `.env.example` 作为模板）
- `backend/database/todo.db`（数据库文件）
- 包含密码或Token的配置文件

### 2. 使用GitHub Secrets

对于生产环境配置，使用GitHub Secrets：

1. 进入仓库 "Settings" → "Secrets and variables" → "Actions"
2. 添加Secret：
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `RENDER_DEPLOY_HOOK`

3. 在workflow中使用：
```yaml
env:
  TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
  TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
```

### 3. 更新依赖

定期更新依赖包以修复安全漏洞：

```bash
cd backend
pip install --upgrade pip
pip list --outdated
pip install --upgrade package-name
```

---

## 🛠️ 常见问题

### Q1: 前端无法连接后端

**原因**：CORS配置或API URL错误

**解决**：
1. 检查 `frontend/js/app.js` 中的 `API_BASE_URL`
2. 检查后端CORS配置
3. 在浏览器控制台查看错误信息

### Q2: Telegram提醒不工作

**原因**：Bot Token或Chat ID错误

**解决**：
1. 重新获取Bot Token和Chat ID
2. 在Render环境变量中更新
3. 重新部署后端
4. 手动发送消息给Bot测试

### Q3: 数据丢失

**原因**：Render免费版的数据可能在停止服务时清空

**解决**：
- 定期备份数据库文件
- 考虑升级到付费版本
- 或使用外部数据库服务

### Q4: 部署失败

**原因**：构建错误、依赖问题、配置错误

**解决**：
1. 查看Render或GitHub Actions日志
2. 本地运行 `pytest` 确保测试通过
3. 检查requirements.txt中的依赖版本

---

## 📈 性能优化

### 1. 启用缓存

对于频繁访问的数据，可以使用Redis缓存：

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    FastAPICache.init(RedisBackend(), prefix="fastapi-cache")
```

### 2. 数据库优化

如果任务数量很大（>10000），考虑：

- 升级到PostgreSQL
- 添加数据库索引
- 使用连接池

### 3. 前端优化

- 压缩CSS和JS文件
- 使用CDN加速静态资源
- 实现懒加载

---

## 🔄 更新和回滚

### 更新应用

```bash
# 拉取最新代码
git pull origin main

# 如果需要，更新依赖
pip install -r requirements.txt

# 重新部署
git push origin main
```

### 回滚到之前版本

1. 在GitHub仓库中找到之前的commit
2. 点击 "Revert" 回滚
3. 推送更改，自动触发部署

---

## 📞 支持

如果遇到问题：

1. 查看本文档的"常见问题"部分
2. 查看Render和GitHub的日志
3. 在GitHub上提交Issue

---

**部署成功！** 🎉

现在你的任务管理系统已经运行在生产环境了。
