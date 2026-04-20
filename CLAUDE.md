# todo-system 项目 Claude 协作指南

## 标准工作流（必须遵守）

每次修改代码时，Claude 必须严格遵循以下工作流：

### 1. 同步代码
```bash
git checkout master
git pull origin master
```

### 2. 修改代码
- 在当前分支进行代码修改
- 确保代码符合项目规范（Black、Flake8、MyPy）

### 3. 本地测试
```bash
# Python 后端测试
cd backend
pytest

# 密钥泄露扫描（重要！）
python scripts/secret-scan.py .
```

### 4. 创建新分支并推送
```bash
git checkout -b feature/xxx 或 fix/xxx
git add -A
git commit -m "<type>: <description>"
git push origin <branch-name>
```

### 5. 等待 CI/CD 通过
```bash
gh run watch --exit-status
```

### 6. 创建 PR（自动审批）
```bash
gh pr create --base master --head <branch-name> --title "<title>" --body "<description>"
gh pr merge <pr-number> --admin --delete-branch
```

### 7. 等待部署通过
```bash
gh run watch --exit-status
```

---

## 密钥安全规范（最高优先级）

### 绝对禁止

1. **禁止在代码中硬编码 API Key、Token、Secret、Password**
2. **禁止在 commit 中包含任何密钥/凭证**
3. **禁止将 .env 文件提交到 Git**

### 正确做法

- 使用环境变量：`os.environ.get("API_KEY")`
- 使用 GitHub Secrets 存储敏感信息
- 本地开发使用 .env 文件（已在 .gitignore 中）

### CI/CD 自动检测

项目 CI/CD 流水线包含密钥扫描步骤（`scripts/secret-scan.py`）：
- **最先运行**（在 lint、test 之前）
- **检测失败则 CI 直接失败**，后续步骤不执行
- 检测硬编码的 API Key、Secret、Token、Password、Private Key 等

### 如果泄露已经发生

1. 立即轮换（rotate）泄露的密钥
2. 使用 `git-filter-repo` 清理 Git 历史
3. 通知相关平台撤销泄露的凭证

---

## 分支命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 功能 | `feature/xxx` | `feature/add-user-auth` |
| 修复 | `fix/xxx` | `fix/e2e-test-selector` |
| 重构 | `refactor/xxx` | `refactor/api-structure` |
| 文档 | `docs/xxx` | `docs/update-readme` |

## Commit 消息规范

```
<type>: <description>

[optional body]
```

| 类型 | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复 bug |
| `refactor` | 重构代码 |
| `docs` | 文档更新 |
| `test` | 测试相关 |
| `chore` | 构建/工具相关 |

---

## CI/CD 流程

项目包含以下工作流：

1. **CI/CD Pipeline** - 密钥扫描 + 代码质量 + 单元测试 + 安全扫描
2. **Deploy to Staging** - 部署到 Staging 环境 + E2E 测试
3. **E2E Tests + Performance** - 独立测试工作流

### CI/CD Pipeline Job 依赖链

```
secret-scan (最先执行)
  ├── lint (Code Quality)
  ├── test (Unit Tests)
  └── security (Trivy Scan)
        └── deploy-preview (PR only)
              └── e2e-light (PR only)
```

### 成功标准

所有工作流必须全部通过（绿色 ✓）才能视为部署成功。

---

## 禁止行为

1. **禁止直接推送到 master** - 必须通过 PR 合并
2. **禁止硬编码密钥** - 必须使用环境变量
3. **禁止跳过测试** - 所有测试必须通过
4. **禁止忽略 CI 失败** - CI 失败必须修复后才能合并

---

*此文件定义了 Claude 协作的标准流程，每次修改代码前务必阅读并遵守。*
