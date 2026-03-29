# Todo System 部署经验教训总结

> 本文档记录了 Todo System 从本地开发到 Render 部署的完整流程，以及过程中踩过的坑和解决方案。

---

## 📋 目录

1. [整体流程概览](#1-整体流程概览)
2. [技术栈](#2-技术栈)
3. [踩过的坑及解决方案](#3-踩过的坑及解决方案)
4. [Render MCP 使用指南](#4-render-mcp-使用指南)
5. [最佳实践](#5-最佳实践)
6. [相关配置](#6-相关配置)

---

## 1. 整体流程概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           部署流程                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   本地开发 ──▶ GitHub ──▶ Render 自动部署 ──▶ 服务上线                 │
│       │           │              │                   │                │
│       │           │              │                   ▼                │
│       │           │              │              数据库迁移             │
│       │           │              │                   │                │
│       │           │              ▼                   ▼                │
│       │           │         webhook 触发      PostgreSQL 数据库        │
│       │           │              │                   │                │
│       ▼           ▼              ▼                   ▼                │
│   代码编写    push commit    pip install        uvicorn 启动            │
│                              requirements.txt                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 技术栈

| 组件 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 后端框架 | FastAPI | 0.109.0 | ASGI web 框架 |
| ASGI 服务器 | Uvicorn | 0.27.0 | 生产环境运行 |
| ORM | SQLAlchemy | 2.0.25 | 数据库 ORM |
| 数据库 | PostgreSQL | - | Render Cloud PostgreSQL |
| 迁移工具 | Alembic | 1.13.1 | 数据库版本管理 |
| Python | 3.11.0 | - | 运行环境 |
| 部署平台 | Render | - | PaaS 平台 |

---

## 3. 踩过的坑及解决方案

### 3.1 Render MCP 连接配置问题

**问题描述：**
- Render MCP 使用 HTTP 传输协议连接到 `https://mcp.render.com/mcp`
- 配置文件中 `command` 字段不能是 `"--"` 这种占位符

**错误配置：**
```json
{
  "mcpServers": {
    "render": {
      "command": "--"  // ❌ 错误：占位符无效
    }
  }
}
```

**正确配置：**
```json
{
  "mcpServers": {
    "render": {
      "url": "https://mcp.render.com/mcp",
      "headers": {
        "Authorization": "Bearer <YOUR_API_KEY>"
      }
    }
  }
}
```

**解决方案：**
- 使用 HTTP 传输方式连接 Render MCP
- 通过 Render Dashboard 创建 API Key
- 在 mcporter 配置中使用 `url` 和 `headers` 字段

---

### 3.2 Python 版本不兼容问题

**问题描述：**
- 部署时使用默认的 Python 3.14.3
- `pydantic-core` 需要从源码编译 Rust 扩展
- Render Free 计划构建环境是只读的，无法编译

**错误日志：**
```
error: failed to create directory `/usr/local/cargo/registry/cache/index.crates.io-1949cf8c6b5b557f`
Read-only file system (os error 30)
💥 maturin failed
```

**原因分析：**
1. Render 的 `PYTHON_VERSION` 环境变量格式要求完整版本号
2. `runtime: python3.11` 语法不生效
3. pydantic==2.10.3 需要源码编译 Rust 扩展

**解决方案：**

1. **设置正确的 Python 版本格式：**
```bash
PYTHON_VERSION=3.11.0  # ✅ 必须完整：major.minor.patch
```

2. **降级依赖版本使用预编译 wheel：**
```txt
# requirements.txt
pydantic==2.5.3  # ✅ 有预编译 wheel
pydantic==2.10.3  # ❌ 需要源码编译
```

3. **在 Render 环境变量中设置：**
```yaml
# render.yaml
services:
  - type: web
    runtime: python3.11  # ❌ 不生效
    # 或使用环境变量
```

**教训：** Render 对 Python 版本格式要求严格，必须提供完整版本号如 `3.11.0`。

---

### 3.3 SQLite 与 PostgreSQL 兼容性问题

**问题描述：**
- 本地开发使用 SQLite 数据库
- Render Free 计划不支持可写文件系统
- SQLite 无法在只读环境中工作

**错误日志：**
```
sqlite3.OperationalError: unable to open database file
```

**解决方案：**

1. **创建 PostgreSQL 数据库：**
   - 登录 Render Dashboard
   - 创建 PostgreSQL 数据库（Free 计划）
   - 获取 `DATABASE_URL`

2. **设置环境变量：**
```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

3. **添加 PostgreSQL 驱动：**
```txt
# requirements.txt
psycopg2-binary==2.9.9  # ✅ PostgreSQL 驱动
```

---

### 3.4 Alembic 迁移配置问题

**问题描述：**
- `alembic.ini` 中硬编码了 SQLite URL
- 构建时 `alembic upgrade head` 使用错误的数据库连接

**原始配置：**
```ini
# alembic.ini
sqlalchemy.url = sqlite:///./database/todo.db  # ❌ 硬编码
```

**解决方案：**

1. **修改 alembic.ini：**
```ini
# alembic.ini
# 注释掉硬编码的 URL，让 env.py 读取环境变量
# sqlalchemy.url = sqlite:///./database/todo.db
```

2. **修改 migrations/env.py：**
```python
import os

def get_url():
    """Get database URL from environment or fallback to config file."""
    return os.environ.get('DATABASE_URL') or config.get_main_option("sqlalchemy.url")

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url = get_url()  # ✅ 使用环境变量
    connectable = engine_from_config(
        {"sqlalchemy.url": url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    # ...
```

3. **分离构建和启动命令：**
```yaml
# render.yaml
buildCommand: pip install -r requirements.txt  # ✅ 构建时不运行迁移
startCommand: sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

**教训：** 永远不要在构建命令中运行数据库迁移，因为构建阶段环境变量可能未生效。

---

### 3.5 DNS 劫持问题

**问题描述：**
- 开发机器使用 Clash VPN
- DNS 被劫持到 198.18.x.x 私有地址
- `nslookup render.com` 返回 `198.18.0.172`

**影响：**
- OpenClaw 浏览器无法访问外部网站
- `render.com` 被解析到错误地址

**解决方案：**

1. **临时关闭代理/VPN**
2. **或切换到"直连"模式**
3. **或在浏览器中直接访问**

**教训：** 使用代理时，AI Agent 的网络请求也会被劫持，需要临时关闭或配置规则。

---

## 4. Render MCP 使用指南

### 4.1 配置 Render MCP

**安装 Render MCP CLI：**
```bash
# 根据你的 AI 工具选择
# Cursor
claude mcp add --transport http render https://mcp.render.com/mcp --header "Authorization: Bearer <YOUR_API_KEY>"

# Claude Desktop
# 编辑配置文件 ~/.config/claude-desktop/mcp.json
```

**配置格式：**
```json
{
  "mcpServers": {
    "render": {
      "url": "https://mcp.render.com/mcp",
      "headers": {
        "Authorization": "Bearer <YOUR_API_KEY>"
      }
    }
  }
}
```

### 4.2 MCP 协议交互流程

Render MCP 使用 JSON-RPC 2.0 协议，需要保持 session：

```python
import requests

API_KEY = "your_api_key"
MCP_URL = "https://mcp.render.com/mcp"
session_id = None

def mcp_request(mcp_payload):
    global session_id
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    
    resp = requests.post(MCP_URL, json=mcp_payload, headers=headers)
    new_session = resp.headers.get("Mcp-Session-Id")
    if new_session:
        session_id = new_session
    return resp.json()

# 1. Initialize
mcp_request({
    "jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "1.0.0"}
    }
})

# 2. Send initialized notification
mcp_request({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

# 3. Select workspace
mcp_request({
    "jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
        "name": "select_workspace",
        "arguments": {"ownerID": "tea-xxxx"}
    }
})

# 4. Call tools
result = mcp_request({
    "jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
        "name": "list_services"
    }
})
```

### 4.3 常用 MCP 工具

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `list_workspaces` | 列出所有工作区 | - |
| `select_workspace` | 选择工作区 | `ownerID` |
| `list_services` | 列出服务 | `ownerId` |
| `list_logs` | 获取日志 | `resource`, `type`, `limit` |
| `update_environment_variables` | 更新环境变量 | `envVars`, `serviceId` |

---

## 5. 最佳实践

### 5.1 Render 部署最佳实践

1. **Python 版本**
   - ✅ 始终指定完整版本号：`3.11.0`
   - ✅ 优先使用有预编译 wheel 的包版本
   - ❌ 避免使用最新版本（可能没有 wheel）

2. **数据库配置**
   - ✅ 使用 PostgreSQL（Render 提供免费 PostgreSQL）
   - ✅ 环境变量使用 `DATABASE_URL`
   - ❌ 不要在代码中硬编码数据库连接

3. **构建命令**
   - ✅ 只做依赖安装
   - ❌ 不要在 buildCommand 中运行数据库迁移
   - ✅ 迁移放在 startCommand 中

4. **依赖管理**
   ```txt
   # requirements.txt 最佳实践
   fastapi==0.109.0        # 固定主版本
   sqlalchemy==2.0.25       # 固定完整版本
   psycopg2-binary==2.9.9  # PostgreSQL 驱动
   ```

### 5.2 GitHub 与 Render 集成

1. **启用自动部署：**
   - 在 Render Dashboard 开启 Auto-Deploy
   - 每次 push 到 master 分支自动触发部署

2. **render.yaml 配置：**
```yaml
services:
  - type: web
    name: todo-system
    runtime: python3.11
    region: ohio
    plan: free
    branch: master
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
```

### 5.3 环境变量管理

```bash
# 必需的环境变量
DATABASE_URL=postgresql://user:pass@host:5432/db
PYTHON_VERSION=3.11.0

# 可选
DEBUG=false
LOG_LEVEL=INFO
```

---

## 6. 相关配置

### 6.1 最终 render.yaml

```yaml
# Render Blueprint 配置
services:
  - type: web
    name: todo-system
    runtime: python3.11
    region: ohio
    plan: free
    branch: master
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    healthCheckPath: /health
```

### 6.2 最终 requirements.txt

```txt
# Python 3.11 兼容版本
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
apscheduler==3.10.4
httpx==0.26.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-multipart==0.0.6
psycopg2-binary==2.9.9
```

### 6.3 环境变量配置（Render Dashboard）

| 变量名 | 值 | 说明 |
|--------|-----|------|
| DATABASE_URL | `postgresql://...` | PostgreSQL 连接字符串 |
| PYTHON_VERSION | `3.11.0` | Python 版本 |

---

## 📞 服务信息

- **访问地址：** https://todo-system-msvx.onrender.com
- **Dashboard：** https://dashboard.render.com/web/srv-d73qddgule4c73emc4l0
- **GitHub：** https://github.com/gdyshi/todo-system

---

## 🔄 后续维护

1. **修改代码后：** push 到 GitHub，自动触发部署
2. **修改配置后：** 需要手动触发部署或更新环境变量
3. **查看日志：** 使用 Render MCP 的 `list_logs` 工具

---

*文档创建时间：2026-03-29*
*作者：贾维斯 AI 助手*
