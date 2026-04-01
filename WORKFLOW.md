# Todo System 项目维护工作流

本文档定义了项目的标准 GitHub 工作流程。

---

## 标准工作流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                        开发阶段 (本地)                               │
├─────────────────────────────────────────────────────────────────────┤
│  1. 创建功能分支 (feature/* 或 fix/*)                               │
│  2. 本地编码修改                                                    │
│  3. 本地测试                                     │
│  4. 推送到 GitHub                                                    │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        PR 阶段 (自动)                                │
├─────────────────────────────────────────────────────────────────────┤
│  ✓ 代码质量检查 (Black, Flake8, MyPy)                               │
│  ✓ 单元测试 + 集成测试                                               │
│  ✓ 安全扫描 (Trivy)                                                 │
│  ✓ Preview 预览部署 (可选)                                           │
│  ✓ 代码审查 (至少 1 人批准)                                          │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      合并阶段 (master)                               │
├─────────────────────────────────────────────────────────────────────┤
│  ✓ 所有检查通过                                                      │
│  ✓ 至少 1 个 Reviewer 批准                                           │
│  ✓ Squash and Merge 到 master                                        │
│  ✓ Staging 环境自动部署                                              │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      生产部署 (手动)                                 │
├─────────────────────────────────────────────────────────────────────┤
│  1. 触发 deploy-production workflow                                  │
│  2. 确认部署                                                         │
│  3. 验证健康检查                                                      │
│  4. 如有问题，执行 rollback                                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 分支策略

### 分支命名规范

| 类型 | 命名格式 | 示例 |
|------|----------|------|
| 功能 | `feature/<name>` | `feature/add-user-auth` |
| 修复 | `fix/<name>` | `fix/login-crash` |
| 测试 | `test/<name>` | `test/e2e-workflow` |
| 文档 | `docs/<name>` | `docs/update-readme` |

### 分支保护规则

**master 分支**已设置以下保护规则：
- ✅ 需要 Pull Request 才能合并
- ✅ 需要 1 人审查批准
- ✅ 新提交时自动清除旧的审查
- ❌ 不强制管理员遵守规则

---

## 本地开发流程

### 1. 创建功能分支

```bash
# 确保本地是最新的
git checkout master
git pull origin master

# 创建功能分支
git checkout -b feature/my-feature
```

### 2. 本地编码

```bash
# 编码...
# 定期提交
git add .
git commit -m "feat: 实现某功能"
```

### 3. 本地测试

```bash
# 后端测试
cd backend
pytest tests/ -v

# E2E 测试 (需要启动服务)
cd ..
npx playwright test

# 代码格式检查
black --check .
flake8 .
mypy .
```

### 4. 推送并创建 PR

```bash
git push origin feature/my-feature

# 创建 PR
gh pr create --title "feat: 实现某功能" --body "描述..."
```

---

## PR 审查流程

### 自动检查项

PR 创建后，GitHub Actions 自动执行：

1. **代码质量检查**
   - Black 格式检查
   - Flake8 Lint 检查
   - MyPy 类型检查

2. **测试**
   - 单元测试
   - 集成测试
   - 测试覆盖率报告

3. **安全扫描**
   - Trivy 漏洞扫描

### 审查要求

- ⚠️ 所有 CI 检查必须通过
- ⚠️ 至少 1 个 Reviewer 批准
- ⚠️ 解决所有对话

---

## 生产部署流程

### 部署到生产

1. 进入 GitHub Actions 页面
2. 选择 `deploy-production` workflow
3. 点击 "Run workflow"
4. 确认执行
5. 等待健康检查通过

### 回滚操作

1. 进入 GitHub Actions 页面
2. 选择 `rollback` workflow
3. 点击 "Run workflow"
4. 选择要回滚的服务
5. 指定部署 ID（可选）
6. 执行回滚

---

## 环境说明

| 环境 | 触发条件 | URL | 用途 |
|------|----------|-----|------|
| Preview | PR 创建/更新 | 随 PR 生成 | 代码预览 |
| Staging | 合并到 master | 自动部署 | 集成测试 |
| Production | 手动触发 | 手动部署 | 正式环境 |

---

## 应急操作

### 紧急修复流程

```bash
# 1. 基于 master 创建 hotfix 分支
git checkout master
git pull origin master
git checkout -b hotfix/urgent-fix

# 2. 修复并测试
# ... 编码 ...
pytest tests/ -v

# 3. 推送并创建紧急 PR
git push origin hotfix/urgent-fix
gh pr create --title "hotfix: 紧急修复" --body "..."

# 4. 合并后立即部署生产
```

---

## 相关文档

- [BRANCH_MANAGEMENT.md](BRANCH_MANAGEMENT.md) - 分支管理详细规则
- [CI_CD_GUIDE.md](CI_CD_GUIDE.md) - CI/CD 配置说明
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 部署指南
