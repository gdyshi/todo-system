# Todo System 测试文档

## 测试概述

本文档说明 Todo System 项目的完整测试套件。

## 测试架构

```
用户 → 前端（HTML+JS） → 后端 API → 编排层 → 执行层 → GLM Coding Lite
```

### 测试类型

| 类型 | 工具 | 覆盖范围 | 运行命令 |
|------|--------|----------|----------|
| 单元测试 | pytest | 编排层、执行层、数据模型 | `./run_tests.sh unit` |
| API 测试 | pytest + httpx | 所有 REST API 端点 | `./run_tests.sh api` |
| 集成测试 | pytest | 双层架构完整流程 | `./run_tests.sh integration` |
| E2E 测试 | Playwright | 浏览器端到端测试 | `./run_tests.sh e2e` |

## 测试数据库

- **路径**：`database/test_todo.db`
- **特点**：独立于生产数据库（`database/todo.db`）
- **自动管理**：每次测试运行前自动清理

## 快速开始

### 1. 安装测试依赖

```bash
cd /home/gdyshi/.openclaw/workspace/todo-system
pip3 install -r requirements-test.txt
```

### 2. 运行所有测试

```bash
# 添加执行权限
chmod +x run_tests.sh

# 运行所有测试
./run_tests.sh all
```

### 3. 运行特定测试

```bash
# 只运行单元测试
./run_tests.sh unit

# 只运行 API 测试
./run_tests.sh api

# 只运行 E2E 测试（需要 Playwright）
./run_tests.sh e2e
```

### 4. 使用 pytest 直接运行

```bash
# 运行单元测试（带覆盖率）
pytest tests/unit/ -v --cov=app --cov-report=html

# 运行 API 测试
pytest tests/api/ -v

# 运行集成测试
pytest tests/integration/ -v

# 运行 E2E 测试（带浏览器窗口）
pytest tests/e2e/ -v --browser chromium --headed

# 运行特定测试文件
pytest tests/unit/orchestrator/test_task_orchestrator.py -v -k "test_classify"
```

## 测试覆盖

### 单元测试

#### 编排层（`tests/unit/orchestrator/`）

| 测试 | 描述 | 状态 |
|------|--------|------|
| `test_orchestrator_init` | 编排器初始化 | ✅ |
| `test_classify_task_work` | 工作任务分类 | ✅ |
| `test_classify_task_education` | 教育任务分类 | ✅ |
| `test_classify_task_life` | 生活任务分类 | ✅ |
| `test_classify_task_with_context_category` | 使用上下文分类 | ✅ |
| `test_determine_task_type_sql` | 确定 SQL 任务类型 | ✅ |
| `test_determine_task_type_api` | 确定 API 任务类型 | ✅ |
| `test_determine_task_type_general` | 确定通用任务类型 | ✅ |
| `test_generate_prompt_for_operation` | 生成 prompt | ✅ |
| `test_adjust_prompt_on_failure` | 失败后调整 prompt | ✅ |
| `test_create_task_basic` | 创建基本任务 | ✅ |
| `test_create_task_with_subtasks` | 创建带子任务的任务 | ✅ |
| `test_complete_task` | 完成任务 | ✅ |
| `test_complete_task_with_incomplete_subtasks` | 完成任务时检查子任务 | ✅ |
| `test_split_task` | 拆解任务 | ✅ |
| `test_generate_and_execute_code_mock` | 生成代码（mock） | ✅ |
| `test_generate_and_execute_code_with_retry` | 失败重试机制 | ✅ |

**覆盖率目标**：90%+

#### 执行层（`tests/unit/executor/`）

| 测试 | 描述 | 状态 |
|------|--------|------|
| `test_code_executor_init` | 执行器初始化 | ✅ |
| `test_build_prompt_with_context` | 构建 prompt（带上下文） | ✅ |
| `test_build_prompt_without_context` | 构建 prompt（无上下文） | ✅ |
| `test_extract_code_from_text_python_block` | 提取 Python 代码块 | ✅ |
| `test_extract_code_from_text_no_block` | 提取代码（无代码块） | ✅ |
| `test_extract_explanation_from_text` | 提取代码说明 | ✅ |
| `test_parse_output_success` | 解析成功输出 | ✅ |
| `test_parse_output_text` | 解析纯文本输出 | ✅ |
| `test_execute_code_task_mock_success` | 执行代码（mock 成功） | ✅ |
| `test_execute_code_task_mock_failure` | 执行代码（mock 失败） | ✅ |
| `test_execute_sql_query_mock` | SQL 查询生成（mock） | ✅ |
| `test_generate_api_endpoint_mock` | API 端点生成（mock） | ✅ |
| `test_execute_code_task_timeout` | 超时处理 | ✅ |
| `test_test_connection_mock` | 连接测试（mock） | ✅ |
| `test_execute_code_task_with_environment` | 环境变量设置 | ✅ |

**覆盖率目标**：85%+

### API 测试（`tests/api/`）

| 测试 | 描述 | 状态 |
|------|--------|------|
| `test_create_task` | 创建任务 | ✅ |
| `test_create_task_invalid_title` | 创建任务（无效标题） | ✅ |
| `test_create_task_auto_category` | 创建任务（自动分类） | ✅ |
| `test_get_tasks` | 获取任务列表 | ✅ |
| `test_get_tasks_with_filter` | 获取任务（带筛选） | ✅ |
| `test_get_task_by_id` | 根据 ID 获取任务 | ✅ |
| `test_get_task_not_found` | 获取任务（不存在） | ✅ |
| `test_update_task` | 更新任务 | ✅ |
| `test_complete_task` | 完成任务 | ✅ |
| `test_complete_task_with_incomplete_subtasks` | 完成任务（未完成子任务） | ✅ |
| `test_delete_task` | 删除任务 | ✅ |
| `test_delete_task_not_found` | 删除任务（不存在） | ✅ |
| `test_split_task` | 拆解任务 | ✅ |
| `test_get_stats` | 获取统计 | ✅ |
| `test_get_mode` | 获取模式 | ✅ |
| `test_set_manual_mode` | 设置手动模式 | ✅ |
| `test_set_auto_mode` | 设置自动模式 | ✅ |
| `test_health_check` | 健康检查 | ✅ |
| `test_root` | 根路径 | ✅ |

**覆盖率目标**：90%+

### E2E 测试（`tests/e2e/`）

**注意**：需要安装 Playwright

#### 创建任务（`test_create_task.spec.ts`）

| 测试 | 描述 | 状态 |
|------|--------|------|
| `test_create_task_success` | 成功创建任务 | ✅ |
| `test_create_task_empty_title` | 创建任务（空标题） | ✅ |
| `test_create_task_with_due_time` | 创建任务（带截止时间） | ✅ |
| `test_create_task_with_subtasks` | 创建任务（带子任务） | ✅ |
| `test_create_task_clears_form` | 创建成功后清空表单 | ✅ |
| `test_create_task_with_location_json` | 创建任务（带地点 JSON） | ✅ |

#### 任务列表（`test_task_list.spec.ts`）

| 测试 | 描述 | 状态 |
|------|--------|------|
| `test_task_list_displays` | 任务列表显示 | ✅ |
| `test_task_list_filter_category` | 筛选分类 | ✅ |
| `test_task_list_filter_status` | 筛选状态 | ✅ |
| `test_task_count_updates` | 任务计数更新 | ✅ |
| `test_task_list_empty_state` | 空状态显示 | ✅ |
| `test_task_list_sorting` | 任务排序 | ✅ |

**覆盖率目标**：80%+

### 集成测试（`tests/integration/`）

| 测试 | 描述 | 状态 |
|------|--------|------|
| `test_architecture_flow_create_task` | 双层架构流程（创建任务） | ✅ |
| `test_architecture_flow_with_retry` | 双层架构（失败重试） | ✅ |
| `test_orchestrator_executor_integration` | 编排层和执行层协作 | ✅ |
| `test_task_lifecycle_with_architecture` | 任务生命周期（含架构调用） | ✅ |
| `test_context_manager_integration` | 上下文管理器集成 | ✅ |
| `test_database_operations_integrity` | 数据库操作完整性 | ✅ |

**覆盖率目标**：85%+

## CI/CD 集成

### GitHub Actions 工作流

创建 `.github/workflows/test.yml`：

```yaml
name: 测试

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: 检出代码
        uses: actions/checkout@v3
      
      - name: 设置 Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: 安装依赖
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: 运行单元测试
        run: pytest tests/unit/ -v --cov=app --cov-report=xml
      
      - name: 运行 API 测试
        run: pytest tests/api/ -v
      
      - name: 运行集成测试
        run: pytest tests/integration/ -v
      
      - name: 上传覆盖率报告
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

## Mock 策略

### 单元测试

所有单元测试使用 mock，**不调用真实 API**：

```python
from unittest.mock import AsyncMock, patch

with patch('asyncio.create_subprocess_exec') as mock_exec:
    # Mock Claude Code CLI 调用
    ...
```

### 集成测试（可选真实 API）

集成测试默认使用 mock。要调用真实 API：

```bash
# 设置环境变量
export TEST_WITH_REAL_API=true

# 运行集成测试
pytest tests/integration/ -v
```

## 测试覆盖率报告

生成覆盖率报告：

```bash
# HTML 报告
pytest tests/ -v --cov=app --cov-report=html

# 查看报告
open htmlcov/index.html
```

覆盖率目标：

- 编排层：90%+
- 执行层：85%+
- 数据模型：95%+
- API：90%+
- E2E：80%+

## 故障排查

### 测试失败

如果测试失败：

1. **检查测试数据库**：
   ```bash
   rm database/test_todo.db
   ```

2. **检查依赖**：
   ```bash
   pip3 list | grep pytest
   pip3 list | grep playwright
   ```

3. **检查后端是否运行**：
   ```bash
   # E2E 测试需要后端运行
   cd backend
   python3 -m uvicorn app.main:app --port 8000
   ```

4. **查看详细日志**：
   ```bash
   pytest tests/ -v -s
   ```

## 下一步

- [ ] 添加更多 E2E 测试场景
- [ ] 提升测试覆盖率到目标值
- [ ] 添加性能测试
- [ ] 添加负载测试
- [ ] 配置 CI/CD 自动运行测试
