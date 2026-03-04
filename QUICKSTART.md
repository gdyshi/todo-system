# 快速配置指南

本文档帮助你快速配置和启动个人任务管理系统。

## ⚡ 5分钟快速开始

### 步骤1：启动系统（2分钟）

```bash
cd /home/gdyshi/.openclaw/workspace/todo-system/backend
./start.sh
```

脚本会自动完成所有配置。

### 步骤2：打开前端（30秒）

在浏览器中打开：
```
/home/gdyshi/.openclaw/workspace/todo-system/frontend/index.html
```

或直接双击 `index.html` 文件。

### 步骤3：测试功能（2分钟）

1. 添加一个测试任务
2. 查看任务列表
3. 尝试完成任务

---

## 🔔 配置Telegram提醒（可选，5分钟）

### 获取Bot Token

1. 打开Telegram
2. 搜索 `@BotFather`
3. 发送 `/newbot`
4. 按提示设置：
   - 机器人名称：`TodoBot`（示例）
   - 用户名：`your_todo_bot`（示例，必须唯一）
5. 复制返回的Bot Token（类似：`1234567890:ABCdefGHIjkLmnoPQRstuVWxyz`）

### 获取Chat ID

1. 在Telegram中搜索 `@userinfobot`
2. 发送任意消息（例如：`hello`）
3. 复制返回的Chat ID（类似：`123456789`）

### 配置环境变量

编辑 `backend/.env` 文件：

```bash
# 找到这两行
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# 填入你的信息
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjkLmnoPQRstuVWxyz
TELEGRAM_CHAT_ID=123456789
```

### 重启服务

如果服务正在运行，按 `Ctrl+C` 停止，然后重新运行 `./start.sh`。

### 测试提醒

1. 打开Telegram，找到你的Bot
2. 发送 `/start`
3. 创建一个带截止时间的任务（例如：5分钟后）
4. 等待提醒（应该在截止时间收到消息）

---

## 🌐 部署到生产环境（可选，10分钟）

### 部署到Render（后端）

#### 1. 注册Render

访问 https://render.com，使用GitHub账号登录。

#### 2. 创建Web Service

1. 点击 "New +" → "Web Service"
2. 选择Fork后的仓库
3. 配置：

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

#### 3. 配置环境变量

在Render的Environment选项卡中添加：

```bash
APP_NAME=Todo System
VERSION=1.0.0
DEBUG=False
DATABASE_PATH=database/todo.db
TELEGRAM_BOT_TOKEN=你的Bot Token
TELEGRAM_CHAT_ID=你的Chat ID
```

#### 4. 部署

点击 "Create Web Service"，等待2-3分钟。

#### 5. 记录URL

部署成功后，你会得到一个URL（类似：`https://todo-system-backend.onrender.com`）。

### 部署到GitHub Pages（前端）

#### 1. 启用GitHub Pages

1. 进入GitHub仓库
2. 点击 "Settings" → "Pages"
3. 配置：
   - Source: `Deploy from a branch`
   - Branch: `main` / `/ (root)`

4. 点击 "Save"

#### 2. 修改API配置

编辑 `frontend/js/app.js`：

```javascript
// 找到这一行
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000/api'
    : '/api';

// 修改为
const API_BASE_URL = 'https://todo-system-backend.onrender.com/api';
```

#### 3. 提交更改

```bash
git add frontend/js/app.js
git commit -m "Update API URL for production"
git push origin main
```

#### 4. 访问

1-2分钟后，访问：`https://your-username.github.io/todo-system/`

---

## ✅ 验证配置

### 本地测试

检查清单：
- [ ] 后端启动成功（看到 `启动成功！` 消息）
- [ ] 前端页面正常打开
- [ ] 可以添加任务
- [ ] 可以完成/删除任务
- [ ] 可以切换分类筛选
- [ ] 统计信息正常显示

### Telegram测试

检查清单：
- [ ] Bot Token配置正确
- [ ] Chat ID配置正确
- [ ] 可以收到Telegram消息
- [ ] 时间提醒正常触发

### 生产环境测试

检查清单：
- [ ] Render部署成功
- [ ] GitHub Pages部署成功
- [ ] 前端可以连接后端
- [ ] 所有功能正常工作

---

## 🛠️ 常见问题

### Q: 后端启动失败

**可能原因**：
- Python版本不对（需要3.11+）
- 依赖安装失败
- 数据库初始化失败

**解决方法**：
```bash
# 检查Python版本
python3 --version

# 手动安装依赖
pip install -r requirements.txt

# 手动初始化数据库
python3 init_db.py
```

### Q: 前端无法连接后端

**可能原因**：
- 后端未启动
- API URL配置错误
- CORS配置问题

**解决方法**：
1. 确认后端运行在 http://localhost:8000
2. 检查浏览器控制台是否有错误
3. 检查Network标签，确认API请求

### Q: Telegram提醒不工作

**可能原因**：
- Bot Token错误
- Chat ID错误
- Bot未启动

**解决方法**：
1. 检查 `.env` 文件配置
2. 在Telegram中搜索你的Bot，发送 `/start`
3. 手动发送消息给Bot，确认能收到回复

### Q: 部署失败

**可能原因**：
- 仓库为空或未推送到GitHub
- Render配置错误
- 环境变量缺失

**解决方法**：
1. 检查GitHub仓库是否有代码
2. 查看Render日志
3. 检查环境变量是否完整

---

## 📚 更多信息

- **README.md** - 完整项目文档
- **API.md** - API接口文档
- **DEPLOYMENT.md** - 详细部署指南
- **PROJECT_SUMMARY.md** - 项目实施总结

---

## 🎉 开始使用

配置完成后，你可以：

1. **添加任务**
   - 填写任务标题
   - 选择分类（或自动检测）
   - 设置截止时间（可选）
   - 添加子任务（可选）

2. **管理任务**
   - 筛选任务（按分类/状态）
   - 完成任务
   - 删除任务
   - 拆解任务

3. **查看统计**
   - 总任务数
   - 完成情况
   - 按分类统计

4. **接收提醒**
   - 时间提醒
   - 地点提醒
   - 通过Telegram接收

---

**祝使用愉快！** 🚀
