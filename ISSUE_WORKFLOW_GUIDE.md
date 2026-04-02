# GitHub Issue 解决流程指南

本文档记录了从 GitHub Issue 创建到最终解决的完整工作流程,以 Issue #8 为例。

---

## 目录

1. [流程概览](#流程概览)
2. [详细步骤](#详细步骤)
3. [常用命令](#常用命令)
4. [最佳实践](#最佳实践)
5. [示例：Issue #8 完整记录](#示例issue-8-完整记录)

---

## 流程概览

```
┌─────────────────┐
│  1. 同步 master  │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 2. 创建功能分支  │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 3. 确认问题      │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 4. 编写解决方案  │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 5. 本地测试      │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 6. 提交代码      │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 7. 创建 PR       │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 8. CI/CD 验证    │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 9. Code Review   │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 10. 合并并关闭   │
└─────────────────┘
```

---

## 详细步骤

### 步骤 1：从 master 同步

确保基于最新的代码进行开发。

```bash
# 切换到 master 分支
git checkout master

# 拉取最新代码
git pull origin master
```

**检查点：**
- [ ] 确认当前分支是 master
- [ ] 确认代码已是最新版本

---

### 步骤 2：创建功能分支

根据 issue 编号创建功能分支。

```bash
# 创建并切换到新分支
git checkout -b fix/issue-{编号}-{简短描述}

# 示例
git checkout -b fix/issue-8-layout-adjustment
```

**分支命名规范：**
- `fix/issue-{编号}-{描述}` - 修复问题
- `feat/issue-{编号}-{描述}` - 新功能
- `refactor/issue-{编号}-{描述}` - 重构

---

### 步骤 3：确认问题

仔细阅读 issue 内容,确认需要解决的问题。

```bash
# 查看 issue 详情
gh issue view {编号}

# 示例
gh issue view 8
```

**确认清单：**
- [ ] 理解 issue 描述的问题
- [ ] 确认问题确实存在
- [ ] 明确解决方案的方向

---

### 步骤 4：编写解决方案

根据 issue 需求修改代码。

**前端项目通常涉及：**
- HTML 结构调整
- CSS 样式修改
- JavaScript 逻辑更新

**编码原则：**
1. 保持代码风格一致
2. 添加必要的注释
3. 考虑响应式设计
4. 保持向后兼容

---

### 步骤 5：本地测试

在提交前进行本地测试。

```bash
# 查看修改的文件
git status

# 查看具体修改内容
git diff

# 如果有测试,运行测试
npm test
# 或
pytest
```

**测试清单：**
- [ ] 功能正常
- [ ] 无控制台错误
- [ ] 响应式布局正常
- [ ] 浏览器兼容性检查

---

### 步骤 6：提交代码

提交代码到本地仓库。

```bash
# 添加所有修改
git add -A

# 提交（使用规范化的提交信息）
git commit -m "feat: 调整布局以满足issue #8需求

- 调整页面布局顺序：任务列表 → 新建任务 → 状态栏
- 任务列表按状态排序：进行中 → 待处理 → 已完成
- 已完成任务默认隐藏，添加显示/隐藏按钮
- 新增状态栏显示统计信息和当前位置
- 优化已完成任务的显示样式（半透明 + 删除线）
- 移除了IP映射和详细统计区块，简化界面"

# 推送到远程
git push -u origin fix/issue-8-layout-adjustment
```

**提交信息规范：**
- `feat:` - 新功能
- `fix:` - 修复问题
- `docs:` - 文档更新
- `style:` - 代码格式
- `refactor:` - 重构
- `test:` - 测试相关

---

### 步骤 7：创建 Pull Request

创建 PR 并关联 issue。

```bash
# 创建 PR
gh pr create --title "fix: 调整布局以满足issue #8需求" --body-file pr_body.md
```

**PR 描述模板：**

```markdown
## 关联Issue
Closes #8

## 改动说明
详细描述做了什么改动...

## 测试步骤
1. 步骤一
2. 步骤二
3. ...

## 截图
（如有界面改动，附上截图）
```

---

### 步骤 8：CI/CD 验证

等待自动化测试完成。

```bash
# 查看 PR 状态
gh pr checks {PR编号}

# 示例
gh pr checks 13

# 查看详细运行日志
gh run view {运行ID}
```

**常见的 CI/CD 检查：**
- ✅ Code Quality Check - 代码质量检查
- ✅ Security Scan - 安全扫描
- ✅ Unit Tests - 单元测试
- ✅ E2E Tests - 端到端测试
- ✅ Deploy Preview - 预览部署

---

### 步骤 9：Code Review

等待团队成员 review。

**Review 检查清单：**
- [ ] 代码逻辑正确
- [ ] 代码风格符合规范
- [ ] 无安全隐患
- [ ] 测试覆盖充分

**处理 Review 意见：**
```bash
# 根据反馈修改代码后
git add -A
git commit -m "fix: 根据 review 意见修改"
git push
```

---

### 步骤 10：合并并关闭 Issue

PR 通过 review 后合并到 master。

```bash
# 合并 PR（在 GitHub 网页上操作或使用命令）
gh pr merge {PR编号} --squash

# 删除本地分支
git checkout master
git branch -d fix/issue-8-layout-adjustment

# 同步 master
git pull origin master
```

---

## 常用命令

### Git 命令

```bash
# 查看分支
git branch -a

# 查看状态
git status

# 查看提交历史
git log --oneline -10

# 查看远程分支
git remote -v

# 强制更新分支
git fetch origin
git reset --hard origin/master
```

### GitHub CLI 命令

```bash
# 列出 issues
gh issue list --state open

# 查看 issue
gh issue view {编号}

# 列出 PRs
gh pr list

# 查看 PR
gh pr view {编号}

# 查看 PR 检查状态
gh pr checks {编号}

# 查看工作流运行
gh run list
gh run view {ID}
```

---

## 最佳实践

### 1. 分支管理

- 每个 issue 创建一个独立分支
- 分支名清晰表达目的
- 定期同步 master 避免冲突

### 2. 提交规范

- 提交信息清晰描述改动
- 使用英文冒号和空格分隔类型和描述
- 多行提交信息详细说明改动点

### 3. PR 规范

- 标题简洁明了
- 描述中包含关联的 issue
- 提供测试步骤和截图
- 及时响应 review 意见

### 4. 测试要求

- 本地测试通过后再提交
- 确保所有 CI/CD 检查通过
- 关注预览环境的实际效果

### 5. 文档更新

- 如有接口变更,更新 API 文档
- 如有使用方式变更,更新用户文档
- 记录重要的技术决策

---

## 示例：Issue #8 完整记录

### Issue 信息

- **编号：** #8
- **标题：** 调整布局
- **描述：**
  - 最上面应该是任务列表
  - 最前面的是正在进行的任务
  - 然后是待执行的任务
  - 已完成的任务默认隐藏
  - 再往下面是新建任务
  - 最下面有一行是状态栏

### 解决过程

#### 1. 同步代码
```bash
git checkout master
git pull origin master
```

#### 2. 创建分支
```bash
git checkout -b fix/issue-8-layout-adjustment
```

#### 3. 查看 Issue
```bash
gh issue view 8
```

#### 4. 修改文件

**修改的文件：**
- `frontend/index.html` - 重新组织页面结构
- `frontend/css/styles.css` - 优化样式,添加状态栏
- `frontend/js/app.js` - 调整任务排序和显示逻辑

**主要改动：**
1. 页面结构重组：任务列表 → 添加任务 → 状态栏
2. 任务列表优化：按状态排序（进行中 → 待处理 → 已完成）
3. 已完成任务默认隐藏,添加显示/隐藏按钮
4. 新增底部状态栏显示统计信息
5. 优化已完成任务的显示样式

#### 5. 提交代码
```bash
git add -A
git commit -m "feat: 调整布局以满足issue #8需求"
git push -u origin fix/issue-8-layout-adjustment
```

#### 6. 创建 PR
```bash
gh pr create --title "fix: 调整布局以满足issue #8需求" --body-file pr_body.md
```

**PR 信息：**
- PR #13
- 链接：https://github.com/gdyshi/todo-system/pull/13

#### 7. CI/CD 验证

所有检查通过：
- ✅ Code Quality Check
- ✅ Security Scan
- ✅ Unit Tests
- ✅ Lightweight E2E Tests
- ✅ Deploy Preview
- ✅ 自动化测试

**预览环境：**
https://todo-system-git-fix-issue-8-layout-adjustment-gdyshis-projects.vercel.app

#### 8. 结果

- PR 成功创建并通过所有检查
- 预览环境部署成功
- 等待 Code Review 后合并

---

## 附录

### 相关文档

- [Git 工作流](./BRANCH_MANAGEMENT.md)
- [CI/CD 指南](./CI_CD_GUIDE.md)
- [API 文档](./API.md)

### 工具链接

- [GitHub 仓库](https://github.com/gdyshi/todo-system)
- [Vercel 部署](https://vercel.com/gdyshis-projects/todo-system)
- [生产环境](https://todo-system-msvx.onrender.com)

---

*最后更新：2026-04-02*
