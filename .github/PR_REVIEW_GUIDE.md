# PR 自动化审查配置指南

## 📋 已配置的自动化流程

### 1. PR Review & Test (`.github/workflows/pr-review.yml`)

此工作流会在创建或更新 PR 时自动触发，执行以下检查：

#### 🔍 代码质量检查
- **Black** - Python 代码格式检查
- **Flake8** - Lint 检查
- **MyPy** - 类型检查
- **Pylint** - 代码质量评分

#### 🧪 自动化测试
- 单元测试（`tests/unit/`）
- 集成测试（`tests/integration/`）
- 测试覆盖率报告
- 上传到 Codecov

#### 🔒 安全扫描
- **Trivy** - 漏洞扫描
- 结果上传到 GitHub Security

#### 🤖 AI 代码审查
- **GitHub CodeQL** - 代码分析和潜在问题检测
- **OpenAI PR Reviewer**（可选，需要配置 API Key）

#### 📊 代码变更分析
- 识别变更的文件
- 分析变更影响
- 触发相关测试

#### 💬 PR 自动评论
- 自动生成审查报告
- 汇总所有检查结果
- 提供改进建议

### 2. CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

此工作流在 push 和 PR 时触发：
- 运行所有测试
- 上传覆盖率报告
- 部署前端到 GitHub Pages

## 🔧 需要配置的 Secrets

### 可选配置

#### OpenAI API Key（用于 AI 代码审查）
1. 访问 https://platform.openai.com/api-keys
2. 创建新的 API Key
3. 在 GitHub 仓库设置中添加 Secret：
   - Name: `OPENAI_API_KEY`
   - Value: 你的 API Key

#### Codecov Token（用于上传覆盖率报告）
1. 访问 https://codecov.io
2. 连接你的 GitHub 仓库
3. 在仓库设置中添加 Secret：
   - Name: `CODECOV_TOKEN`
   - Value: Codecov 提供的 token

## 🚀 使用方法

### 创建 PR
当你创建或更新 PR 时，自动化流程会自动触发：

1. **代码质量检查** - 验证代码格式和规范
2. **自动化测试** - 运行所有测试
3. **安全扫描** - 检查潜在漏洞
4. **AI 代码审查** - 智能分析代码问题
5. **自动评论** - 在 PR 中生成审查报告

### 查看审查结果
在 PR 页面你可以看到：
- ✅/❌ 每个检查的状态
- 📊 测试覆盖率报告
- 🔒 安全扫描结果
- 💬 自动生成的评论和建议

### 修复问题
如果某个检查失败：
1. 查看失败原因（点击 Details）
2. 修复代码问题
3. 提交新的 commit
4. 自动化流程会重新运行

## 🎯 最佳实践

### 1. 本地预检查
在推送前，可以在本地运行相同的检查：

```bash
# 代码格式检查
black --check backend/app/

# Lint 检查
flake8 backend/app/

# 类型检查
mypy backend/app/

# 运行测试
pytest tests/ -v
```

### 2. 分支保护规则
在 GitHub 仓库设置中配置分支保护：
- Settings → Branches → Add rule
- 保护 `main`/`master` 分支
- 要求 PR 通过所有检查后才能合并

### 3. 审查策略
- 先看自动化审查结果
- 关注 ⚠️ 和 ❌ 的项目
- 根据自动评论改进代码
- 人工审查业务逻辑和架构设计

## 🔍 GitHub 自带代码审查

### GitHub Copilot（付费）
如果你有 Copilot Business 订阅：
1. 在仓库设置中启用 Copilot
2. 在 PR 中使用 Copilot 的代码审查功能
3. Copilot 会自动在 PR 中提供建议

### GitHub CodeQL（免费）
已配置在 PR 流程中，自动分析代码中的潜在问题：
- 安全漏洞
- 性能问题
- 代码异味
- 最佳实践违反

## 📈 监控和优化

### 查看历史记录
- Actions 标签页：查看所有工作流运行记录
- Security 标签页：查看安全扫描结果
- Insights 标签页：查看代码贡献统计

### 优化流程
根据实际情况调整：
- 增加或移除检查项
- 调整测试阈值
- 优化 AI 审查提示词
- 添加自定义检查脚本

## ❓ 常见问题

### Q: 为什么 OpenAI 审查没有运行？
A: 需要在仓库设置中配置 `OPENAI_API_KEY` Secret。

### Q: 如何跳过某些检查？
A: 在 commit message 中添加 `[skip ci]` 跳过 CI 流程。

### Q: 如何修改审查规则？
A: 编辑 `.github/workflows/pr-review.yml` 文件。

### Q: 测试覆盖率不够怎么办？
A: 在 `pr-review.yml` 中添加覆盖率检查，并设置最低阈值。

## 📚 参考资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [GitHub CodeQL](https://codeql.github.com/docs/)
- [Trivy 漏洞扫描](https://aquasecurity.github.io/trivy/)
- [Codecov 覆盖率报告](https://codecov.io/)
- [GitHub Copilot](https://github.com/features/copilot)

---

**最后更新**: 2026-03-04
