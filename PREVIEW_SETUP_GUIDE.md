# Preview Environment 配置指南

本文档说明如何配置 Vercel Preview Environment。

## 需要的 Secrets

在 GitHub 仓库的 `Settings > Secrets and variables > Actions` 中添加以下 secrets：

### 1. Vercel 配置

#### 获取 VERCEL_TOKEN
1. 访问 https://vercel.com/account/tokens
2. 点击 "Create Token"
3. 输入 Token 名称（如：github-actions）
4. 选择权限范围（推荐：Full Account）
5. 复制生成的 Token

#### 获取 VERCEL_ORG_ID
```bash
# 安装 Vercel CLI
npm install -g vercel

# 登录
vercel login

# 进入项目目录
cd todo-system/frontend

# 链接项目
vercel link

# 查看组织信息
cat .vercel/project.json
```

或访问 https://vercel.com/dashboard，找到你的 Team/Organization，复制 Organization ID。

#### 获取 VERCEL_PROJECT_ID
```bash
# 在项目目录执行
vercel project list

# 或查看
cat .vercel/project.json
```

---

## GitHub Secrets 配置步骤

1. 打开仓库: https://github.com/gdyshi/todo-system/settings/secrets/actions
2. 点击 "New repository secret"
3. 添加以下 secrets：

| Secret Name | 获取方式 |
|-------------|----------|
| `VERCEL_TOKEN` | Vercel Account 页面 |
| `VERCEL_ORG_ID` | `vercel project list` 或 .vercel/project.json |
| `VERCEL_PROJECT_ID` | `vercel project list` 或 .vercel/project.json |

---

## Vercel 项目配置

### 如果还没有 Vercel 项目：

1. 访问 https://vercel.com
2. 注册/登录 GitHub 账号
3. 点击 "Import Project"
4. 选择 `gdyshi/todo-system`
5. 配置项目：
   - **Framework Preset**: Other
   - **Root Directory**: ./frontend
   - **Build Command**: 空（或 `# build`）
   - **Output Directory**: ./
6. 点击 "Deploy"

### 重要配置

确保 Vercel 项目设置中：
- **Build Command**: 留空（静态文件不需要构建）
- **Environment Variables**: 配置 `API_BASE_URL` 指向后端 Preview URL

---

## 本地测试

配置完成后，可以手动触发 workflow 测试：

```bash
# 查看 workflow 文件是否正确
cat .github/workflows/preview.yml
```

---

## 验证

PR 创建后，应该能看到：
1. Vercel 自动部署前端预览
2. PR 下自动评论预览链接
3. Preview 环境成功/失败状态

---

## 故障排除

### Vercel Token 无效
- 确认 Token 没有过期
- 确认 Token 有足够的权限

### 部署失败
- 检查 Vercel 项目设置
- 查看 GitHub Actions 日志
- 确认 `VERCEL_ORG_ID` 和 `VERCEL_PROJECT_ID` 正确

### Preview URL 不工作
- 检查 `API_BASE_URL` 是否正确配置
- 确认后端预览服务已启动
