# Todo System 项目指南

## 项目概览

这是一个基于双层架构设计的智能任务管理系统，支持自动分类、任务拆解、时间/地点提醒等功能。

## 知识图谱

项目包含知识图谱，位于 `.understand-anything/knowledge-graph.json`。
在修改代码前，请先读取该文件了解项目结构。

## 架构设计

### 双层架构

```
用户界面（Web）
    ↓ HTTP/JSON
编排层（Orchestrator Layer）
    ├─ TaskOrchestrator: 理解用户意图、拆解任务
    ├─ ContextManager: IP/位置检测、模式切换
    └─ ReminderScheduler: 时间/地点提醒调度
    ↓
执行层（Executor Layer）
    ├─ TaskExecutor: 数据库操作
    ├─ CodeExecutor: AI 代码生成
    └─ ExternalServices: Telegram、IP API
    ↓
数据库（SQLite）
```

### 模块职责

| 模块 | 职责 | 文件位置 |
|------|------|----------|
| API 层 | HTTP 端点定义 | `backend/app/api/` |
| 编排层 | 业务逻辑、上下文管理 | `backend/app/orchestrator/` |
| 执行层 | 数据操作、外部服务 | `backend/app/executor/` |
| 模型层 | SQLAlchemy ORM | `backend/app/models/` |
| 前端 | 单页应用 | `frontend/` |

## 编码规则

- 修改代码后，必须同步更新 `.understand-anything/knowledge-graph.json`
- 新增函数需要在图谱中添加对应节点
- 修改依赖关系需要更新图谱中的边
- 改完后运行测试确保通过

## 测试

```bash
# 后端单元测试
cd backend
pytest tests/ -v

# E2E 测试
npx playwright test

# 完整测试脚本
./run_tests.sh
```

## 启动命令

```bash
# 后端
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 前端（开发）
cd frontend
python -m http.server 8000
```

## 部署信息

- 后端：Render (https://todo-system-msvx.onrender.com)
- 前端：Vercel (https://todo-system-psi.vercel.app)
- CI/CD：GitHub Actions

## 关键设计决策

1. **双层架构**：编排层处理业务逻辑，执行层处理技术实现，职责分离
2. **智能分类**：根据 IP/地理位置自动切换工作/生活/教育模式
3. **双重提醒**：时间和地点两种触发方式，通过 APScheduler 调度
4. **增量更新**：知识图谱支持增量更新，无需每次全量重建
