# 🌳 分支管理策略

## 📋 当前分支状态（清理后）

### 本地分支
- `master` - 唯一主分支

### 远程分支
- `master` - 默认主分支
- `feature/code-review-test` - 当前工作分支
- `gh-pages` - GitHub Pages 部署分支

---

## 🎯 分支命名规范

### 主分支
- `master` - 永远稳定的主分支

### 功能分支
```
feature/功能名称-简要描述
```
例如：
- `feature/add-user-auth`
- `feature/improve-search`
- `feature/refactor-service-layer`

### 修复分支
```
fix/问题描述-修复方式
```
例如：
- `fix/login-timeout`
- `fix/payment-crash`

### 紧急修复分支
```
hotfix/紧急问题描述
```
例如：
- `hotfix/payment-security`

---

## 🔄 工作流程

### 开发流程
1. **从 master 创建新分支**
   ```bash
   git checkout master
   git pull origin master
   git checkout -b feature/add-new-feature
   ```

2. **开发并提交**
   ```bash
   git add .
   git commit -m "feature: add new feature"
   ```

3. **推送分支**
   ```bash
   git push origin feature/add-new-feature
   ```

4. **创建 Pull Request**
   - 标题格式：`type: short-description`
   - 例如：`feat: 添加用户认证功能`
   - `fix: 修复登录超时问题`

5. **代码审查**
   - 通过 PR 自动化流程
   - 人工审查

6. **合并到 master**
   - 使用 GitHub 的 "Merge pull request" 按钮
   - 不要直接 push 到 master

7. **删除分支**
   ```bash
   git checkout master
   git branch -d feature/add-new-feature
   git push origin --delete feature/add-new-feature
   ```

### 紧急修复流程
1. **从 master 创建 hotfix 分支**
   ```bash
   git checkout master
   git pull origin master
   git checkout -b hotfix/security-patch
   ```

2. **修复并推送**
   ```bash
   git add .
   git commit -m "hotfix: security patch"
   git push origin hotfix/security-patch
   ```

3. **创建 PR 并合并**
   - 同正常开发流程

4. **立即删除分支**
   - 热修复完成后立即删除分支

---

## 📌 最佳实践

### ✅ 应该做的
- **每个功能一个分支**：不要在一个分支中混入多个功能
- **分支命名清晰**：从分支名就能看出这是什么工作
- **及时删除分支**：合并后 24 小时内删除
- **PR 标题规范**：`type: description` 格式
- **频繁提交**：小步快跑，每个提交都是可审查的
- **提交信息规范**：
  - `feat:` 新功能
  - `fix:` 修复 Bug
  - `docs:` 文档更新
  - `style:` 代码格式调整（不影响功能）
  - `refactor:` 重构（既不是新增功能，也不是修复 Bug）
  - `test:` 测试相关
  - `chore:` 构建过程或辅助工具的变动

### ❌ 不应该做的
- **直接 push 到 master**：所有改动必须经过 PR
- **在废弃分支上工作**：使用最新、干净的分支
- **合并后不删除分支**：积累的废弃分支会让仓库变乱
- **分支命名随意**：不要用 `test`、`temp`、`fix-fix` 等无意义名称
- **超长的分支**：保持分支名简短、有描述性
- **包含敏感信息**：分支名不要包含密码、密钥等

---

## 🔧 分支管理脚本

### 清理脚本
```bash
#!/bin/bash
# 删除所有已合并的本地分支
git branch --merged | grep -v "\*" | grep -v master | xargs git branch -d

# 删除所有已合并的远程分支
git branch -r --merged | grep -v "\*" | grep -v "origin/master" | grep -v "origin/gh-pages" | sed 's|origin/||' | xargs -I {} git push origin --delete {}

# 清理本地引用
git remote prune origin
```

### 检查脚本
```bash
#!/bin/bash
# 列出所有分支
echo "=== 本地分支 ==="
git branch -a

echo ""
echo "=== 远程分支 ==="
git branch -r

echo ""
echo "=== 已合并但未删除的分支 ==="
git branch --merged | grep -v "\*" | grep -v master

echo ""
echo "=== 未合并的分支 ==="
git branch --no-merged | grep -v "\*" | grep -v master
```

---

## 🚨 常见问题

### Q1: 如何处理多个相关的 Bug 修复？
**A**: 创建一个 `fix/xxx` 分支，在同一个分支中修复所有相关的 Bug，然后一次性合并。

### Q2: 如何在开发中更新 master 的最新代码？
**A**:
```bash
git checkout master
git pull origin master
git checkout feature/your-feature
git rebase master
git push origin feature/your-feature --force
```

### Q3: PR 合并冲突怎么办？
**A**:
1. 在 master 上更新代码：`git pull origin master`
2. 切换到功能分支：`git checkout feature/your-feature`
3. 合并 master：`git merge master`
4. 手动解决冲突
5. 提交并推送：`git push`

### Q4: 如何回滚一个错误的合并？
**A**:
```bash
git log --oneline
# 找到要回滚到的提交 ID，例如 abc1234
git revert abc1234
git push origin master
```

### Q5: 为什么有 `gh-pages` 分支？
**A**: 这是 GitHub Pages 自动部署创建的分支，用于托管静态网站，不需要手动管理。

---

## 📚 参考资料

- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [约定式提交](https://www.conventionalcommits.org/)
- [Git 分支管理最佳实践](https://setroginix.medium.com/git-branch-management-best-practices-d8bed09e0689)

---

**最后更新**: 2026-03-10
**维护者**: 贾维斯
