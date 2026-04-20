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

# 前端测试（如有）
cd frontend
npm test
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
gh pr merge <pr-number> --merge --delete-branch
```

### 7. 等待部署通过
```bash
gh run watch --exit-status
```

---

## 分支命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 功能 | `feature/xxx` | `feature/add-user-auth` |
| 修复 | `fix/xxx` | `fix/e2e-test-selector` |
| 重构 | `refactor/xxx` | `refactor/api-structure` |
| 文档 | `docs/xxx` | `docs/update-readme` |

---

## Commit 消息规范

```
<type>: <description>

[optional body]

[optional footer]
```

### Type 类型

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

1. **CI/CD Pipeline** - 代码质量检查 + 单元测试 + 安全扫描
2. **Deploy to Staging** - 部署到 Staging 环境 + E2E 测试
3. **E2E Tests + Performance** - 独立测试工作流

### 成功标准

所有工作流必须全部通过（绿色 ✓）才能视为部署成功。

---

## 常见问题

### E2E 测试失败
- 检查测试代码是否与前端元素匹配
- 查看 `tests/e2e/` 目录下的测试文件

### Vercel 部署失败
- 检查 Vercel CLI 版本（需要 47.2.2+）
- 检查 `vercel.json` 配置

### 类型检查失败
- 运行 `mypy backend/` 查看详细错误
- 确保 Optional 类型正确处理

---

## 禁止行为

1. **禁止直接推送到 master** - 必须通过 PR 合并
2. **禁止跳过测试** - 所有测试必须通过
3. **禁止忽略 CI 失败** - CI 失败必须修复后才能合并

---

*此文件定义了 Claude 协作的标准流程，每次修改代码前务必阅读并遵守。*
