# 个人任务管理系统

基于双层架构设计的智能任务管理系统，支持自动分类、任务拆解、时间/地点提醒等功能。

## ✨ 特性

- **双层架构设计**：编排层 + 执行层，上下文专业化分工
- **智能分类**：根据IP/地理位置自动切换工作/生活/教育模式
- **任务管理**：添加任务、拆分子任务、标记完成、设置优先级
- **双重提醒**：基于时间和地点的智能提醒（Telegram）
- **完全自动化**：从开发到部署的完整CI/CD流程
- **Web界面**：响应式设计，支持移动端

## 🏗️ 架构设计

### 双层架构

```
用户界面（Web）
    ↓ HTTP/JSON
编排层（Orchestration Layer）
    ├─ 任务管理器：理解用户意图、拆解任务
    ├─ 上下文管理器：IP/位置检测、模式切换
    └─ 提醒调度器：时间/地点提醒调度
    ↓
执行层（Execution Layer）
    ├─ 数据库操作
    ├─ 外部服务调用
    └─ 业务逻辑执行
    ↓
数据库（SQLite）
```

### 技术栈

| 组件 | 技术 |
|------|------|
| **后端** | FastAPI + SQLAlchemy + APScheduler |
| **前端** | HTML + CSS + Vanilla JavaScript |
| **数据库** | SQLite |
| **部署** | Render（后端） + GitHub Pages（前端） |
| **CI/CD** | GitHub Actions |
| **通知** | Telegram Bot |

## 🚀 快速开始

### 本地开发

1. **克隆仓库**
```bash
git clone https://github.com/your-username/todo-system.git
cd todo-system
```

2. **安装依赖**
```bash
cd backend
pip install -r requirements.txt
```

3. **初始化数据库**
```bash
python -c "from app.models import init_db; init_db()"
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，配置Telegram等
```

5. **启动后端**
```bash
uvicorn app.main:app --reload
```

6. **访问前端**
```bash
# 方法1：直接打开
open frontend/index.html

# 方法2：使用http服务器
cd frontend
python -m http.server 8080
```

访问：http://localhost:8080

## 📱 配置提醒功能

### 1. 获取Telegram Bot Token

1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称
4. 获取Bot Token

### 2. 获取Chat ID

1. 在Telegram中搜索 `@userinfobot`
2. 发送任意消息
3. 获取你的Chat ID

### 3. 配置环境变量

在 `backend/.env` 文件中添加：

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### 4. 测试提醒

重启后端服务，创建一个带截止时间的任务，等待提醒触发。

## 🔧 部署到生产环境

### 自动部署（推荐）

1. **Fork本仓库**到你的GitHub账号

2. **连接到Render**
   - 访问 https://render.com
   - 注册账号
   - 连接GitHub账号
   - 点击"New +" -> "Web Service"
   - 选择本仓库
   - 配置构建和启动命令

3. **配置环境变量**
   在Render中添加所有环境变量（参考 `.env.example`）

4. **获取Deploy Hook**
   - 在Render服务页面找到Deploy Hook URL
   - 复制并添加到GitHub Secrets

5. **启用GitHub Pages**
   - 在GitHub仓库设置中启用Pages
   - 选择 `frontend` 目录作为发布源

### 手动部署

**后端部署到Render**

```bash
# 1. 构建Docker镜像（可选）
docker build -t todo-system backend/

# 2. 或直接部署源代码
git push origin main
# Render会自动部署
```

**前端部署到GitHub Pages**

```bash
cd frontend
git add .
git commit -m "Update frontend"
git push origin main
# GitHub Pages会自动部署
```

## 📊 使用说明

### 添加任务

1. 填写任务标题（必填）
2. 选择分类（自动/工作/生活/教育）
3. 设置优先级、截止时间、地点提醒（可选）
4. 添加子任务（可选）
5. 点击"添加任务"

### 任务分类

系统会根据你的IP和地理位置自动分类：

- **工作**：在公司IP下创建的任务
- **生活**：在家IP下创建的任务
- **教育**：在学校IP下创建的任务

你也可以手动切换分类模式。

### 任务拆解

1. 找到要拆解的任务
2. 点击"⚡ 拆解任务"按钮
3. 输入子任务（每行一个）
4. 系统会自动创建子任务

### 完成任务

1. 任务的所有子任务必须先完成
2. 点击"✓ 完成"按钮
3. 任务状态更新为"已完成"

### 删除任务

点击"🗑️ 删除"按钮删除任务（会级联删除子任务）。

## 🧪 运行测试

```bash
cd backend
pytest tests/ -v
```

## 🔍 PR 自动化审查

项目已配置完整的自动化 PR 审查流程，在创建或更新 Pull Request 时自动触发。

### 自动化检查项

✅ **代码质量检查**
- Black - Python 代码格式检查
- Flake8 - Lint 检查
- MyPy - 类型检查
- Pylint - 代码质量评分

✅ **自动化测试**
- 单元测试（`tests/unit/`）
- 集成测试（`tests/integration/`）
- 测试覆盖率报告

✅ **安全扫描**
- Trivy - 漏洞扫描
- 结果上传到 GitHub Security

🤖 **AI 代码审查**
- GitHub CodeQL - 代码分析和潜在问题检测
- OpenAI PR Reviewer（可选，需配置 API Key）

📊 **代码变更分析**
- 识别变更的文件
- 分析变更影响

💬 **PR 自动评论**
- 自动生成审查报告
- 汇总所有检查结果

### 使用方法

1. 创建 Pull Request 到 `main` 或 `master` 分支
2. 自动化流程自动触发
3. 在 PR 页面查看所有检查结果
4. 根据审查建议改进代码

### 配置 Secrets（可选）

如果需要 OpenAI 代码审查：
1. 访问 https://platform.openai.com/api-keys
2. 创建 API Key
3. 在 GitHub 仓库设置中添加 `OPENAI_API_KEY` Secret

详细配置说明请查看 [.github/PR_REVIEW_GUIDE.md](.github/PR_REVIEW_GUIDE.md)

## 📝 开发指南

### 目录结构

```
todo-system/
├── backend/
│   ├── app/
│   │   ├── orchestrator/      # 编排层
│   │   ├── executor/           # 执行层
│   │   ├── models/             # 数据模型
│   │   ├── api/                # API路由
│   │   └── main.py             # 应用入口
│   ├── tests/                  # 测试
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/styles.css
│   └── js/app.js
└── .github/workflows/           # CI/CD配置
```

### 添加新功能

1. **编排层**：在 `app/orchestrator/` 中添加业务逻辑
2. **执行层**：在 `app/executor/` 中添加数据操作
3. API端点**：在 `app/api/` 中添加路由
4. **前端**：在 `frontend/js/` 中添加交互逻辑

## 🔒 安全说明

- 敏感信息存储在环境变量中，不要提交到Git
- 使用HTTPS访问生产环境
- 定期更新依赖包
- 数据库文件不应暴露在公开目录

## 📈 性能优化

- SQLite适合个人使用，生产环境可升级到PostgreSQL
- 使用APScheduler进行任务调度，避免重复检查
- 前端静态资源压缩优化加载速度

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- 架构设计灵感来自Datawhale的《OpenClaw + Codex/Claude Code》文章
- 使用FastAPI构建高性能后端
- 使用Tailwind CSS构建响应式界面

---

**开发状态**：✅ 完成核心功能
**最后更新**：2026-03-01
**版本**：1.0.0
