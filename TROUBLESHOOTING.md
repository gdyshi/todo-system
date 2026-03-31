# Todo System 部署调试记录

> 本文档记录了前后端联调过程中踩过的坑及解决方案。

---

## 📋 问题汇总

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| [Vercel 部署失败](#1-vercel-部署-root-directory-错误) | Root Directory 配置错误 | 清空 Root Directory |
| [前端 API 请求失败](#2-前端连接后端失败) | API 地址硬编码 localhost | 环境自动切换 |
| [浏览器显示旧代码](#3-浏览器缓存问题) | CDN 缓存未更新 | 硬刷新或清空缓存 |
| [预览部署 URL 混淆](#4-预览部署-url-混淆) | 多个预览部署 URL | 使用正确的生产 URL |

---

## 1. Vercel 部署 Root Directory 错误

### 错误信息
```
Error: NOW_SANDBOX_WORKER_ROOTDIR_NOT_EXIST
The specified Root Directory "frontend" does not exist.
```

### 问题原因
Vercel 项目设置中，`Root Directory` 配置为 `frontend`，但代码结构中 `frontend` 目录已经在根目录下，所以实际路径变成了 `frontend/frontend`。

### 排查过程
```bash
# 通过 Vercel API 查看项目配置
curl -H "Authorization: Bearer $VERCEL_TOKEN" \
  https://api.vercel.com/v2/projects/prj_UEp6AHgPteUEQmeRsjvdztFs0gqE

# 结果显示 rootDirectory: "frontend"
```

### 解决方案
1. **方法一：通过 Dashboard 修改**
   - 打开 https://vercel.com/gdyshi/todo-system/settings
   - 找到 **Root Directory** 设置
   - 清空或改为 `.`

2. **方法二：通过 API 修改**
```bash
curl -X PATCH "https://api.vercel.com/v2/projects/{projectId}" \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rootDirectory": null}'
```

---

## 2. 前端连接后端失败

### 错误现象
- 前端页面加载正常
- 但点击"加载任务"显示"加载失败"
- 后端 API (`/api/tasks`) 单独测试正常

### 问题原因
前端 `app.js` 中 API 地址硬编码为 `localhost`：
```javascript
// 错误代码 ❌
const API_BASE_URL = 'http://localhost:8000/api';
```

当前端部署到 Vercel 后，用户浏览器会请求 `http://localhost:8000/api`，这显然是访问不到的。

### 排查过程
1. 打开浏览器 Console 执行：
```javascript
console.log('hostname:', window.location.hostname);
console.log('API_BASE_URL:', API_BASE_URL);
```

2. 发现 `hostname` 是 `todo-system-psi.vercel.app`，但 `API_BASE_URL` 是 `http://localhost:8000/api`

3. 检查 GitHub 代码确认修复是否已推送

### 解决方案
修改 `frontend/js/app.js`，添加环境检测：
```javascript
// 正确代码 ✅
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api'
    : 'https://todo-system-msvx.onrender.com/api';
```

---

## 3. 浏览器缓存问题

### 问题现象
- 代码已经推送到 GitHub
- Vercel 显示部署成功
- 但浏览器显示的还是旧代码

### 原因分析
1. **Vercel CDN 缓存**
   - 静态资源会被 CDN 缓存
   - 默认缓存时间较长

2. **浏览器缓存**
   - 浏览器会缓存 JS 文件
   - 304 Not Modified 响应

### 解决方案

**方法一：硬刷新**
```
Ctrl + Shift + R (Windows)
Cmd + Shift + R (Mac)
```

**方法二：清空缓存并硬重新加载**
1. 打开开发者工具 (F12)
2. 右键点击刷新按钮
3. 选择"清空缓存并硬重新加载"

**方法三：隐身模式**
```
Ctrl + Shift + N (Chrome)
Cmd + Shift + P (Firefox)
```

**方法四：清除特定域名缓存**
1. 打开开发者工具
2. Network 标签
3. 勾选 "Disable cache"
4. 刷新页面

---

## 4. 预览部署 URL 混淆

### 问题现象
- 有多个 Vercel 部署 URL
- 访问旧 URL 显示"加载失败"
- 不知道哪个是正式生产环境

### 部署 URL 列表
| URL | 类型 | 代码版本 |
|-----|------|----------|
| `todo-system-psi.vercel.app` | **生产环境** | master 分支（最新）|
| `todo-system-xxx.vercel.app` | 预览环境 | PR 分支 |
| `gh-pages` | GitHub Pages | 已废弃 |

### 确认方法
1. **通过 Vercel Dashboard**
   - 打开 https://vercel.com/gdyshi/todo-system
   - 找到带 ⭐ 或 "Production" 标签的部署

2. **通过 API 查询**
```bash
curl -H "Authorization: Bearer $VERCEL_TOKEN" \
  "https://api.vercel.com/v6/deployments?projectId={projectId}&limit=5"
```
查看 `target: "production"` 的部署。

---

## 5. DNS 劫持问题（开发环境）

### 问题现象
- 使用 Clash VPN
- `nslookup render.com` 返回 `198.18.0.172`
- AI Agent 无法访问外部网站

### 原因
Clash 默认启用 DNS 劫持，将域名解析到 198.18.x.x 保留地址。

### 解决方案
1. **临时关闭代理**
2. **切换到"直连"模式**
3. **在代理软件中添加规则放行目标域名**

---

## 6. Vercel API 部署配置问题

### 问题
使用 Vercel API 触发部署时收到错误：
```
Invalid request: missing required property `name`
```

### 解决方案
确保请求体包含 `name` 字段：
```json
{
  "name": "todo-system",
  "gitSource": {
    "type": "github",
    "repoId": "1172122671",
    "ref": "refs/heads/master"
  }
}
```

注意：`teamId` 不应该在请求体中，应该放在 URL 或 Header 中。

---

## 📝 调试技巧

### 1. 检查 API 响应
```javascript
// 在浏览器 Console 中执行
fetch('https://todo-system-msvx.onrender.com/api/tasks')
  .then(res => res.json())
  .then(console.log)
  .catch(console.error)
```

### 2. 检查 CORS 配置
```javascript
// 浏览器 Console
fetch('https://todo-system-msvx.onrender.com/api/tasks', {
  method: 'OPTIONS'
}).then(res => {
  console.log('CORS Headers:', {
    'access-control-allow-origin': res.headers.get('access-control-allow-origin'),
    'access-control-allow-credentials': res.headers.get('access-control-allow-credentials')
  });
})
```

### 3. 检查环境变量
```javascript
console.log('All env vars containing API:', 
  Object.keys(process.env).filter(k => k.includes('API'))
);
```

---

## 📅 创建时间
2026-03-31

## 🔄 更新记录
- 2026-03-31: 初始版本
