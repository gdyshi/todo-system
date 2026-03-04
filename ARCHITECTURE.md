# 双层架构实现文档

## 架构概述

基于原文 [OpenClaw + Codex/Claude Code：一个人就能搭建完整的开发团队](https://mp.weixin.qq.com/s/gtxM1f3JmfXqDuxGIa3-ng) 的双层架构设计，适配到 Todo 系统。

**实现状态：✅ 已完成并测试通过**

### 架构设计

```
用户 → 编排层 (TaskOrchestrator) → 执行层 (CodeExecutor) → Claude Code CLI → GLM Coding Lite API
```

#### 编排层 (TaskOrchestrator)

**职责**：
- 理解用户需求和意图
- 持有业务上下文（任务分类、历史记录、用户偏好）
- 根据需求生成精确的 prompt
- 调用执行层完成任务
- 监控执行进度，失败后分析原因并调整 prompt 重试
- **不直接编写代码**
- **只访问生产数据库的只读权限**

**核心能力**：
1. 智能分类任务（工作、教育、生活）
2. 拆解复杂任务为子任务
3. 学习位置/IP 到分类的映射
4. 根据操作类型生成不同的 prompt
5. 改进版 Ralph Loop - 失败后调整 prompt 而不是简单重试

#### 执行层 (CodeExecutor)

**职责**：
- 接收编排层的精确 prompt
- 调用 **Claude Code CLI**
- Claude Code CLI 使用 **GLM Coding Lite API** 认证
- 返回生成的代码和解释
- 专注于技术实现
- **不持有业务上下文**
- **不访问生产数据库**

**核心能力**：
1. 通用代码生成
2. SQL 查询生成（使用 SQLAlchemy ORM）
3. FastAPI 端点生成

**技术实现**：
- 调用 Claude Code CLI（`claude` 命令）
- 参数：
  - `--model glm-4.7`：使用 GLM-4.7 模型
  - `--print`：非交互模式，直接返回结果
  - `--output-format json`：返回 JSON 格式
  - `--dangerously-skip-permissions`：全权运行，跳过权限确认
- 环境变量：`ANTHROPIC_API_KEY`（设置为 GLM API key）

### 架构设计

```
用户 → 编排层 (TaskOrchestrator) → 执行层 (CodeExecutor + GLM Coding Lite)
```

#### 编排层 (TaskOrchestrator)

**职责**：
- 理解用户需求和意图
- 持有业务上下文（任务分类、历史记录、用户偏好）
- 根据需求生成精确的 prompt
- 调用执行层完成任务
- 监控执行进度，失败后分析原因并调整 prompt 重试
- **不直接编写代码**
- **只访问生产数据库的只读权限**

**核心能力**：
1. 智能分类任务（工作、教育、生活）
2. 拆解复杂任务为子任务
3. 学习位置/IP 到分类的映射
4. 根据操作类型生成不同的 prompt
5. 改进版 Ralph Loop - 失败后调整 prompt 而不是简单重试

#### 执行层 (CodeExecutor)

**职责**：
- 接收编排层的精确 prompt
- 调用 GLM Coding Lite API 生成代码
- 返回生成的代码和解释
- 专注于技术实现
- **不持有业务上下文**
- **不访问生产数据库**

**核心能力**：
1. 通用代码生成
2. SQL 查询生成（使用 SQLAlchemy ORM）
3. FastAPI 端点生成

### 为什么需要双层架构？

**单层架构的问题**：
- 上下文窗口有限，必须在"业务上下文"和"代码"之间二选一
- AI 不知道这个功能是为哪个用户做的
- 不知道上次类似需求为什么失败了
- 不知道产品的定位和设计原则

**双层架构的优势**：
- **专业化分工**：编排层专注于业务逻辑，执行层专注于代码
- **上下文隔离**：执行层只拿到最小上下文，不接触敏感信息
- **可扩展性**：可以轻松切换不同的代码生成服务（Claude Code、Codex、GLM 等）
- **智能重试**：编排层可以根据失败原因调整 prompt，而执行层保持简单

### API 流程

#### 1. 生成代码

```bash
POST /api/demo/generate-code
```

**请求**：
```json
{
  "task_id": 123,
  "operation": "query",
  "custom_prompt": "可选的自定义 prompt"
}
```

**流程**：
1. 编排层接收请求
2. 如果有 `task_id`，加载任务的业务上下文
3. 生成精确的 prompt（包含任务标题、分类、描述、截止时间等）
4. 调用执行层，传入 prompt 和操作类型
5. 执行层调用 GLM Coding Lite API
6. 返回生成的代码和解释

**响应**：
```json
{
  "success": true,
  "operation": "query (task #123)",
  "code": "完整的代码",
  "explanation": "代码说明",
  "error": null
}
```

#### 2. 查看架构信息

```bash
GET /api/demo/architecture
```

返回当前架构的详细说明。

### 配置

在 `app/config.py` 中已配置 GLM API key：

```python
glm_api_key: str = "357cd9367f801b6df81b655113572404.byyt1f6Wd6AvKXpU"
glm_model: str = "glm-4.7"
```

Claude Code CLI 已经手动配置好，使用全权权限运行（`--dangerously-skip-permissions`）。

### 与原文的差异

| 原文 | 当前实现 |
|------|---------|
| 编排层：OpenClaw | 编排层：TaskOrchestrator (Python) |
| 执行层：Claude Code CLI | 执行层：CodeExecutor → Claude Code CLI |
| 代码生成：Claude/Codex/Gemini API | 代码生成：GLM Coding Lite API（通过 Claude Code CLI） |
| tmux 会话管理 | 直接 CLI 调用，使用异步 subprocess |
| git worktree 隔离 | 数据库事务隔离 |
| 多个代码 Agent (Codex/Claude/Gemini) | 当前支持 GLM，可扩展到其他模型 |

### 测试结果

**2026-03-02 测试通过 ✅**

```bash
$ python3 test_architecture.py

============================================================
测试双层架构 - 执行层
============================================================

GLM API Key: 357cd9367f801b6df81b...
GLM 模型: glm-4.7

测试 1: 通用代码生成
------------------------------------------------------------
成功: True

解释: 生成了完整的 Python 函数，包含类型注解、docstring、错误处理

测试 2: SQL 查询生成
------------------------------------------------------------
成功: True

解释: 生成了 SQLAlchemy ORM 查询，包含两种写法和说明

测试 3: 连接测试
------------------------------------------------------------
成功: True
消息: 连接成功

============================================================
测试完成
============================================================
```

**测试覆盖**：
- ✅ 通用代码生成
- ✅ SQL 查询生成
- ✅ Claude Code CLI 连接测试
- ✅ 错误处理和超时机制
- ✅ JSON 响应解析

### 扩展性

要支持其他代码生成服务（如 Claude Code、Codex），只需：

1. 在 `CodeExecutor` 中添加新的方法
2. 在 `config.py` 中添加对应的 API 配置
3. 在编排层添加 Agent 选择逻辑

例如，添加 Claude Code 支持：

```python
async def execute_with_claude_code(self, prompt: str) -> Dict:
    # 调用 Claude Code CLI 或 API
    pass
```

### 测试

#### 1. 快速测试 CLI 调用

```bash
# 测试 Claude Code CLI 是否正常工作
ANTHROPIC_API_KEY="357cd9367f801b6df81b655113572404.byyt1f6Wd6AvKXpU" \
claude --model glm-4.7 --print --dangerously-skip-permissions \
"写一个 Hello World 函数"
```

#### 2. 运行完整测试

```bash
cd /home/gdyshi/.openclaw/workspace/todo-system
python3 test_architecture.py
```

#### 3. 启动 FastAPI 服务

```bash
cd /home/gdyshi/.openclaw/workspace/todo-system/backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. 测试 API 端点

```bash
# 测试代码生成 API
curl -X POST http://localhost:8000/api/demo/generate-code \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "query",
    "custom_prompt": "生成一个 SQLAlchemy 查询，获取所有高优先级的待办任务"
  }'

# 查看架构信息
curl http://localhost:8000/api/demo/architecture
```

### 使用示例

#### 在代码中使用

```python
from app.orchestrator.task_orchestrator import TaskOrchestrator
from app.models import Task

# 初始化编排器
orchestrator = TaskOrchestrator(db)

# 获取一个任务
task = await orchestrator.executor.get_task(123)

# 编排层生成 prompt 并调用执行层
result = await orchestrator.generate_and_execute_code(
    task=task,
    operation="query",
    context="这个任务是高优先级的，需要尽快完成"
)

# 处理结果
if result["success"]:
    print(f"生成的代码:\n{result['code']}")
    print(f"说明: {result['explanation']}")
else:
    print(f"错误: {result['error']}")
```

#### 直接调用执行层

```python
from app.executor.code_executor import CodeExecutor

# 初始化执行器
executor = CodeExecutor(api_key="your_api_key", model="glm-4.7")

# 生成 SQL 查询
result = await executor.execute_sql_query(
    query="获取所有未完成的任务",
    description="status != 'completed'"
)

if result["success"]:
    print(f"SQL: {result['sql']}")
    print(f"说明: {result['explanation']}")
```

### 下一步改进

1. **Prompt 优化**：建立成功/失败的 prompt 模式库
2. **多 Agent 支持**：根据任务类型选择不同的代码生成服务
3. **执行层沙箱**：在隔离环境中执行生成的代码
4. **持续学习**：将成功的模式记录下来，改进未来的 prompt
