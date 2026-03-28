# Step 2: Staging 环境 + 数据库迁移配置指南

## 概述

本步骤配置自动化部署到 Staging 环境，包括：
- 后端自动部署到 Render
- 前端自动部署到 Vercel
- 数据库自动迁移
- E2E 集成测试
- 性能基准测试

---

## 需要的 Secrets

在 GitHub 仓库的 `Settings > Secrets and variables > Actions` 中添加以下 secrets：

### 1. Render Staging 配置

#### 获取 RENDER_STAGING_DEPLOY_HOOK

1. 访问 https://dashboard.render.com
2. 创建新的 Web Service：
   - **Name**: `todo-api-staging`
   - **Environment**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`

3. 在 Service 设置中找到 "Deploy Hook"
4. 复制 Deploy Hook URL

#### 获取 STAGING_DATABASE_URL

1. 在 Render 中创建 PostgreSQL 数据库
2. 复制连接字符串

### 2. Vercel Staging 配置

使用之前配置的 secrets：
- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`

---

## GitHub Secrets 配置步骤

1. 打开仓库: https://github.com/gdyshi/todo-system/settings/secrets/actions
2. 点击 "New repository secret"
3. 添加以下 secrets：

| Secret Name | 获取方式 |
|-------------|----------|
| `RENDER_STAGING_DEPLOY_HOOK` | Render Dashboard > Deploy Hook |
| `STAGING_DATABASE_URL` | Render Dashboard > Database Connection String |

---

## 数据库迁移配置

### 初始化 Alembic

```bash
cd backend
alembic init -t async migrations
```

### 创建第一个迁移

```bash
alembic revision --autogenerate -m "Initial migration"
```

### 应用迁移

```bash
alembic upgrade head
```

---

## 工作流程

### 自动触发条件

- 代码 push 到 `master` 或 `main` 分支
- 手动触发 (workflow_dispatch)

### 执行步骤

1. **后端部署** → Render Staging
2. **前端部署** → Vercel Staging
3. **数据库迁移** → 自动运行 Alembic
4. **E2E 测试** → 集成测试
5. **性能测试** → 基准测试
6. **部署总结** → 生成报告

---

## 验证部署

部署完成后，可以访问：

- **后端 API**: https://todo-api-staging.onrender.com
- **前端**: https://staging.todo-system.vercel.app
- **API 文档**: https://todo-api-staging.onrender.com/docs

---

## 故障排除

### 部署失败

1. 检查 Render Deploy Hook 是否正确
2. 查看 GitHub Actions 日志
3. 确认数据库连接字符串正确

### 数据库迁移失败

1. 检查 Alembic 配置
2. 查看迁移文件是否正确
3. 确认数据库权限

### 健康检查失败

1. 确认后端服务已启动
2. 检查 `/health` 端点是否可访问
3. 查看 Render 日志

---

## 下一步

配置完成后，可以继续 **Step 3: E2E 测试 + 性能基准**
