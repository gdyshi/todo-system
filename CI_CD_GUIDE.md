# Todo System CI/CD 完整部署指南

## 项目概览

**Todo System** 是一个全栈任务管理应用，采用现代化的 CI/CD 流水线架构。

- **后端**：FastAPI + PostgreSQL (Render)
- **前端**：静态 HTML/JS (Vercel)
- **测试**：Playwright E2E + 性能基准
- **部署**：自动化 + 手动控制

---

## 第一部分：本地开发环境搭建

### 1.1 环境要求

```
Python 3.11.0
Node.js 20+
npm 10+
Git
```

### 1.2 后端启动

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**验证**：访问 http://localhost:8000/docs 看到 Swagger UI

### 1.3 前端启动

```bash
cd frontend

# 启动静态服务器
python -m http.server 8000
```

**验证**：访问 http://localhost:8000 看到任务列表页面

### 1.4 运行 E2E 测试

```bash
# 安装依赖
npm install

# 运行测试
npx playwright test

# 查看报告
npx playwright show-report
```

---

## 第二部分：CI/CD 流水线详解

### 2.1 四个步骤概览

```
┌─────────────────────────────────────────────────────────────┐
│                    Todo System CI/CD 流水线                  │
└─────────────────────────────────────────────────────────────┘

Step 1: Preview Environment
├─ 每个 PR 自动创建预览部署
├─ 前端：Vercel preview URL
├─ 后端：Render preview URL
└─ 用途：代码审查、测试

Step 2: Staging 环境
├─ master 分支自动部署到 Staging
├─ 完整的数据库迁移
├─ 性能测试
└─ 用途：集成测试、性能验证

Step 3: E2E 测试 + 性能基准
├─ 自动运行 8 个 E2E 测试
├─ 测试覆盖：创建、编辑、筛选、计数
├─ 性能指标：LCP、FCP、CLS、TTFB
└─ 用途：质量保证

Step 4: 手动发布 + 回滚
├─ 手动触发生产部署
├─ 部署前健康检查
├─ 支持一键回滚
└─ 用途：生产环境控制
```

### 2.2 Workflow 文件说明

| 文件 | 触发条件 | 功能 |
|------|---------|------|
| `ci-cd.yml` | 代码推送 | 基础 CI 检查 |
| `preview.yml` | PR 创建 | 预览部署 |
| `deploy-staging.yml` | master 推送 | Staging 部署 |
| `e2e-test.yml` | master 推送 | E2E 测试 |
| `deploy-production.yml` | 手动触发 | 生产部署 |
| `rollback.yml` | 手动触发 | 回滚操作 |

---

## 第三部分：GitHub 配置

### 3.1 必需的 Secrets

在 GitHub 仓库设置中添加以下 Secrets：
https://github.com/gdyshi/todo-system/settings/secrets/actions

| Secret 名称 | 值 | 用途 |
|------------|-----|------|
| `RENDER_API_KEY` | 从 Render 仪表板获取 | Render 部署控制 |
| `VERCEL_TOKEN` | 从 Vercel 仪表板获取 | Vercel 部署控制 |

**配置步骤**：
1. 打开 https://github.com/gdyshi/todo-system/settings/secrets/actions
2. 点击 "New repository secret"
3. 输入 Secret 名称和值
4. 点击 "Add secret"

### 3.2 环境变量配置

#### Render 后端环境变量

在 Render 仪表板配置：
https://dashboard.render.com/services/srv-d73qddgule4c73emc4l0

```
DATABASE_URL=postgresql://[用户名]:[密码]@[主机]/[数据库]
PYTHON_VERSION=3.11.0
```

#### Vercel 前端环境变量

在 Vercel 仪表板配置：
https://vercel.com/gdyshi/todo-system/settings/environment-variables

```
# 无需特殊环境变量，前端自动检测 API 地址
```

---

## 第四部分：部署操作指南

### 4.1 自动部署流程

**代码推送 → 自动触发**

```bash
git add .
git commit -m "feat: 新功能"
git push origin master
```

自动执行：
1. ✅ CI/CD Pipeline（代码检查）
2. ✅ Deploy to Staging（Staging 部署）
3. ✅ E2E Tests（自动化测试）

### 4.2 手动发布到生产

**步骤 1**：打开 GitHub Actions
https://github.com/gdyshi/todo-system/actions

**步骤 2**：选择 "Manual Production Deploy"

**步骤 3**：点击 "Run workflow"

**步骤 4**：填写参数
- `environment`: 选择 `production`
- `confirm`: 勾选 `true`

**步骤 5**：点击 "Run workflow"

**预期结果**：
- ✅ 部署前健康检查（50s）
- ✅ 部署执行（34s）
- ✅ 部署验证通过

### 4.3 回滚操作

**步骤 1**：打开 GitHub Actions
https://github.com/gdyshi/todo-system/actions

**步骤 2**：选择 "Rollback"

**步骤 3**：点击 "Run workflow"

**步骤 4**：填写参数
- `service`: 选择 `backend` / `frontend` / `both`
- `deploy_id`: 留空（自动选择最新部署）
- `confirm`: 勾选 `true`

**步骤 5**：点击 "Run workflow"

**预期结果**：
- ✅ 获取当前部署 ID
- ✅ 执行回滚
- ✅ 健康检查验证

---

## 第五部分：监控和故障排查

### 5.1 查看部署日志

**Render 后端日志**：
https://dashboard.render.com/services/srv-d73qddgule4c73emc4l0/logs

**Vercel 前端日志**：
https://vercel.com/gdyshi/todo-system/deployments

**GitHub Actions 日志**：
https://github.com/gdyshi/todo-system/actions

### 5.2 常见问题

#### 问题 1：E2E 测试超时

**原因**：前端或后端服务不可用

**解决**：
```bash
# 检查后端
curl https://todo-system-msvx.onrender.com/health

# 检查前端
curl https://todo-system-psi.vercel.app
```

#### 问题 2：部署失败

**原因**：依赖安装失败或环境变量缺失

**解决**：
1. 检查 GitHub Secrets 是否配置
2. 查看 Render/Vercel 部署日志
3. 检查 requirements.txt 或 package.json

#### 问题 3：回滚失败

**原因**：RENDER_API_KEY 未配置或过期

**解决**：
1. 确认 GitHub Secret 已配置
2. 检查 API Key 是否有效
3. 查看 GitHub Actions 日志

---

## 第六部分：性能指标

### 6.1 E2E 测试覆盖

| 测试 | 功能 | 预期结果 |
|------|------|---------|
| 成功创建任务 | 创建新任务 | ✅ 任务出现在列表 |
| 创建任务（空标题） | 验证必填字段 | ✅ 显示错误提示 |
| 创建任务（带截止时间） | 设置截止日期 | ✅ 任务显示截止时间 |
| 创建任务（带子任务） | 添加子任务 | ✅ 子任务显示在任务下 |
| 创建成功后表单清空 | 表单重置 | ✅ 输入框清空 |
| 任务列表显示 | 列表渲染 | ✅ 任务列表可见 |
| 任务列表筛选 | 按分类筛选 | ✅ 筛选结果正确 |
| 任务计数显示 | 计数器 | ✅ 显示正确数量 |

### 6.2 性能基准

| 指标 | 目标 | 当前 |
|------|------|------|
| LCP (Largest Contentful Paint) | < 2.5s | ✅ |
| FCP (First Contentful Paint) | < 2s | ✅ |
| CLS (Cumulative Layout Shift) | < 0.1 | ✅ |
| TTFB (Time to First Byte) | < 800ms | ✅ |
| TTI (Time to Interactive) | < 3.5s | ✅ |
| API 响应时间 | < 500ms | ✅ |

---

## 第七部分：改进建议

### 7.1 已完成的优化

✅ **自动化程度高**
- 代码推送自动触发测试和部署
- 无需手动干预

✅ **安全性好**
- 生产部署需要手动确认
- 支持一键回滚

✅ **可观测性强**
- 部署前后健康检查
- 完整的日志记录

### 7.2 可进一步改进的方向

#### 建议 1：添加性能监控告警
```yaml
# 在 e2e-test.yml 中添加
- name: Performance Alert
  if: failure()
  run: |
    # 发送告警到 Slack/钉钉
    curl -X POST ${{ secrets.ALERT_WEBHOOK }} \
      -d "性能测试失败"
```

#### 建议 2：增加 E2E 测试覆盖
```typescript
// 添加更多测试场景
- 编辑任务
- 删除任务
- 标记完成
- 搜索功能
- 排序功能
```

#### 建议 3：添加蓝绿部署
```yaml
# 支持同时运行两个版本
# 流量逐步切换
# 快速回滚
```

#### 建议 4：集成 SonarQube 代码质量检查
```yaml
- name: SonarQube Scan
  run: sonar-scanner
```

#### 建议 5：添加数据库备份
```yaml
- name: Backup Database
  before: deploy-production
  run: |
    # 部署前自动备份
    pg_dump $DATABASE_URL > backup.sql
```

#### 建议 6：添加灰度发布
```yaml
# 先发布到 10% 用户
# 监控 30 分钟
# 无问题则全量发布
```

---

## 第八部分：快速参考

### 常用命令

```bash
# 本地开发
cd backend && uvicorn app.main:app --reload
cd frontend && python -m http.server 8000

# 运行测试
npx playwright test
npx playwright test --debug

# 查看测试报告
npx playwright show-report

# 推送代码
git push origin master

# 查看部署状态
gh run list --repo gdyshi/todo-system

# 查看部署日志
gh run view <RUN_ID> --repo gdyshi/todo-system --log
```

### 重要链接

| 资源 | 链接 |
|------|------|
| GitHub 仓库 | https://github.com/gdyshi/todo-system |
| 后端 API | https://todo-system-msvx.onrender.com |
| 前端应用 | https://todo-system-psi.vercel.app |
| GitHub Actions | https://github.com/gdyshi/todo-system/actions |
| Render 仪表板 | https://dashboard.render.com |
| Vercel 仪表板 | https://vercel.com/gdyshi/todo-system |

---

## 总结

这个 CI/CD 流水线实现了：

✅ **完全自动化**：代码推送自动测试和部署
✅ **高可靠性**：多层次的检查和验证
✅ **快速反馈**：问题立即发现
✅ **安全部署**：生产环境需要确认
✅ **快速回滚**：一键恢复到上一版本

**下一步**：根据建议 7.2 中的改进方向，逐步增强流水线的功能。
