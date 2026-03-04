"""TaskOrchestrator 单元测试"""
import pytest
from app.orchestrator.task_orchestrator import TaskOrchestrator
from app.models import Task
from app.orchestrator.context_manager import Context
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_orchestrator_init(test_db):
    """测试：编排器初始化"""
    orchestrator = TaskOrchestrator(test_db)
    
    assert orchestrator.executor is not None
    assert orchestrator.context_manager is not None
    assert orchestrator.reminder_scheduler is not None


@pytest.mark.asyncio
async def test_classify_task_work(test_db):
    """测试：工作任务分类"""
    orchestrator = TaskOrchestrator(test_db)
    
    result = orchestrator._classify_task(
        {"title": "完成项目报告"},
        Context()
    )
    
    assert result == "work"


@pytest.mark.asyncio
async def test_classify_task_education(test_db):
    """测试：教育任务分类"""
    orchestrator = TaskOrchestrator(test_db)
    
    result = orchestrator._classify_task(
        {"title": "学习 Python 编程"},
        Context()
    )
    
    assert result == "education"


@pytest.mark.asyncio
async def test_classify_task_life(test_db):
    """测试：生活任务分类"""
    orchestrator = TaskOrchestrator(test_db)
    
    result = orchestrator._classify_task(
        {"title": "去超市买菜"},
        Context()
    )
    
    assert result == "life"


@pytest.mark.asyncio
async def test_classify_task_with_context_category(test_db):
    """测试：使用上下文中的分类"""
    orchestrator = TaskOrchestrator(test_db)
    
    context = Context(category="work")
    result = orchestrator._classify_task(
        {"title": "随便的任务"},
        context
    )
    
    # 上下文优先
    assert result == "work"


@pytest.mark.asyncio
async def test_determine_task_type_sql(test_db):
    """测试：确定任务类型 - SQL"""
    orchestrator = TaskOrchestrator(test_db)
    
    result = orchestrator._determine_task_type("生成 SQL 查询")
    
    assert result == "sql"


@pytest.mark.asyncio
async def test_determine_task_type_api(test_db):
    """测试：确定任务类型 - API"""
    orchestrator = TaskOrchestrator(test_db)
    
    result = orchestrator._determine_task_type("创建 API 端点")
    
    assert result == "api"


@pytest.mark.asyncio
async def test_determine_task_type_general(test_db):
    """测试：确定任务类型 - 通用"""
    orchestrator = TaskOrchestrator(test_db)
    
    result = orchestrator._determine_task_type("写一个函数")
    
    assert result == "general"


@pytest.mark.asyncio
async def test_generate_prompt_for_operation(test_db):
    """测试：生成 prompt"""
    orchestrator = TaskOrchestrator(test_db)
    
    task = Task(
        id=1,
        title="测试任务",
        description="这是一个测试描述",
        category="work",
        status="pending",
        priority=5,
        due_time=datetime.utcnow() + timedelta(hours=1)
    )
    
    prompt = orchestrator._generate_prompt_for_operation(
        task=task,
        operation="query",
        context="额外的上下文信息"
    )
    
    # 验证 prompt 包含关键信息
    assert "测试任务" in prompt
    assert "work" in prompt
    assert "这是一个测试描述" in prompt
    assert "额外的上下文信息" in prompt
    assert "生成一个 SQLAlchemy 查询" in prompt


@pytest.mark.asyncio
async def test_adjust_prompt_on_failure(test_db):
    """测试：失败后调整 prompt"""
    orchestrator = TaskOrchestrator(test_db)
    
    original_prompt = "原始 prompt"
    error = "API 错误"
    
    adjusted_prompt = orchestrator._adjust_prompt_on_failure(original_prompt, error)
    
    # 验证调整后的 prompt 包含错误信息
    assert error in adjusted_prompt
    assert "根据上述错误重新生成" in adjusted_prompt
    assert "原始任务" in adjusted_prompt
    assert original_prompt in adjusted_prompt


@pytest.mark.asyncio
async def test_create_task_basic(test_db):
    """测试：创建基本任务"""
    orchestrator = TaskOrchestrator(test_db)
    
    task = await orchestrator.create_task(
        title="测试任务",
        context=Context(category="work"),
        description="测试描述"
    )
    
    assert task.id is not None
    assert task.title == "测试任务"
    assert task.category == "work"
    assert task.description == "测试描述"
    assert task.status == "pending"


@pytest.mark.asyncio
async def test_create_task_with_subtasks(test_db):
    """测试：创建带子任务的任务"""
    orchestrator = TaskOrchestrator(test_db)
    
    task = await orchestrator.create_task(
        title="父任务",
        context=Context(category="work"),
        subtasks=["子任务1", "子任务2"]
    )
    
    assert task.id is not None
    
    # 获取所有任务，验证子任务
    all_tasks = await orchestrator.executor.get_all_tasks()
    parent_task = next((t for t in all_tasks if t.title == "父任务"), None)
    
    assert parent_task is not None
    
    # 验证子任务数量（2个子任务 + 1个父任务 = 3）
    work_tasks = [t for t in all_tasks if t.category == "work"]
    assert len(work_tasks) >= 2  # 至少有父任务和部分子任务


@pytest.mark.asyncio
async def test_complete_task(test_db):
    """测试：完成任务"""
    orchestrator = TaskOrchestrator(test_db)
    
    # 先创建任务
    task = await orchestrator.create_task(
        title="待完成任务",
        context=Context(category="work")
    )
    
    # 完成任务
    completed_task = await orchestrator.complete_task(task.id)
    
    assert completed_task.status == "completed"


@pytest.mark.asyncio
async def test_complete_task_with_incomplete_subtasks(test_db):
    """测试：完成任务时有未完成的子任务应该报错"""
    orchestrator = TaskOrchestrator(test_db)
    
    # 创建带子任务的任务
    parent_task = await orchestrator.create_task(
        title="父任务",
        context=Context(category="work"),
        subtasks=["子任务1", "子任务2"]
    )
    
    # 只完成一个子任务
    all_tasks = await orchestrator.executor.get_all_tasks()
    subtask = [t for t in all_tasks if t.parent_id == parent_task.id][0]
    await orchestrator.complete_task(subtask.id)
    
    # 尝试完成父任务（应该失败）
    with pytest.raises(ValueError, match="请先完成所有子任务"):
        await orchestrator.complete_task(parent_task.id)


@pytest.mark.asyncio
async def test_split_task(test_db):
    """测试：拆解任务"""
    orchestrator = TaskOrchestrator(test_db)
    
    # 先创建任务
    parent_task = await orchestrator.create_task(
        title="待拆解任务",
        context=Context(category="work")
    )
    
    # 拆解任务
    subtask_titles = ["子任务1", "子任务2", "子任务3"]
    subtasks = await orchestrator.split_task(
        task_id=parent_task.id,
        subtasks=subtask_titles,
        context=Context(category="work")
    )
    
    assert len(subtasks) == 3
    assert subtasks[0].title == "子任务1"
    assert subtasks[1].title == "子任务2"
    assert subtasks[2].title == "子任务3"


@pytest.mark.asyncio
async def test_generate_and_execute_code_mock(test_db):
    """测试：生成 prompt 并调用执行层（使用 mock）"""
    from unittest.mock import AsyncMock, patch
    
    orchestrator = TaskOrchestrator(test_db)
    
    task = Task(
        id=1,
        title="代码生成测试",
        category="work",
        status="pending"
    )
    
    # Mock 执行层的响应
    mock_result = {
        "success": True,
        "code": "生成的代码",
        "explanation": "代码说明"
    }
    
    with patch.object(orchestrator.executor, 'execute_code_generation', new_callable=AsyncMock(return_value=mock_result)):
        result = await orchestrator.generate_and_execute_code(
            task=task,
            operation="query"
        )
        
        assert result["success"] == True
        assert result["code"] == "生成的代码"
        assert result["explanation"] == "代码说明"


@pytest.mark.asyncio
async def test_generate_and_execute_code_with_retry(test_db):
    """测试：失败后重试（使用 mock）"""
    from unittest.mock import AsyncMock, patch
    
    orchestrator = TaskOrchestrator(test_db)
    
    task = Task(
        id=1,
        title="代码生成测试",
        category="work",
        status="pending"
    )
    
    # 第一次调用失败
    mock_result_fail = {
        "success": False,
        "error": "API 错误",
        "code": None,
        "explanation": None
    }
    
    # 第二次调用成功
    mock_result_success = {
        "success": True,
        "code": "生成的代码",
        "explanation": "代码说明"
    }
    
    with patch.object(orchestrator.executor, 'execute_code_generation', new_callable=AsyncMock(side_effect=[mock_result_fail, mock_result_success])):
        result = await orchestrator.generate_and_execute_code(
            task=task,
            operation="query"
        )
        
        # 应该在第二次调用时成功
        assert result["success"] == True
        assert result["code"] == "生成的代码"
