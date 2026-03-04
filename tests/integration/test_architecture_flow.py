"""集成测试：双层架构完整流程"""
import pytest
import os
from app.orchestrator.task_orchestrator import TaskOrchestrator
from app.models import Task
from app.orchestrator.context_manager import Context
from datetime import datetime


@pytest.mark.integration
@pytest.mark.asyncio
async def test_architecture_flow_create_task(test_db, mock_api_key):
    """
    集成测试：双层架构完整流程 - 创建任务
    
    编排层 → 生成 prompt → 执行层 → 生成代码
    """
    from unittest.mock import AsyncMock, patch
    
    orchestrator = TaskOrchestrator(test_db)
    
    # Mock 执行层的响应
    mock_result = {
        "success": True,
        "code": "session.query(Task).filter(...).all()",
        "explanation": "SQLAlchemy 查询代码"
    }
    
    with patch.object(orchestrator.executor, 'execute_code_generation', new_callable=AsyncMock(return_value=mock_result)):
        # 创建任务
        task = await orchestrator.create_task(
            title="集成测试任务",
            context=Context(category="work"),
            description="这是一个集成测试"
        )
        
        assert task.id is not None
        assert task.title == "集成测试任务"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_architecture_flow_with_retry(test_db, mock_api_key):
    """
    集成测试：双层架构 - 失败重试
    
    第一次失败 → 调整 prompt → 第二次成功
    """
    from unittest.mock import AsyncMock, patch
    
    orchestrator = TaskOrchestrator(test_db)
    
    task = Task(
        id=1,
        title="重试测试任务",
        category="work",
        status="pending"
    )
    
    # 第一次调用失败
    mock_result_fail = {
        "success": False,
        "error": "API 超时",
        "code": None,
        "explanation": None
    }
    
    # 第二次调用成功
    mock_result_success = {
        "success": True,
        "code": "查询代码",
        "explanation": "代码说明"
    }
    
    with patch.object(orchestrator.executor, 'execute_code_generation', new_callable=AsyncMock(side_effect=[mock_result_fail, mock_result_success])):
        result = await orchestrator.generate_and_execute_code(
            task=task,
            operation="query"
        )
        
        # 应该在第二次调用时成功
        assert result["success"] == True
        assert result["code"] == "查询代码"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_orchestrator_executor_integration(test_db, mock_api_key):
    """
    集成测试：编排层和执行层协作
    
    创建任务 → 编排层生成 prompt → 执行层调用 API
    """
    from unittest.mock import AsyncMock, patch
    
    orchestrator = TaskOrchestrator(test_db)
    
    # 创建任务
    task = await orchestrator.create_task(
        title="协作测试",
        context=Context(category="education")
    )
    
    # Mock 执行层返回 SQL 代码
    mock_sql_result = {
        "success": True,
        "sql": "SELECT * FROM tasks WHERE category = 'education'",
        "explanation": "查询所有教育任务",
        "type": "sql"
    }
    
    with patch.object(orchestrator.executor, 'execute_code_generation', new_callable=AsyncMock(return_value=mock_sql_result)):
        # 调用编排层生成 SQL
        result = await orchestrator.generate_and_execute_code(
            task=task,
            operation="query",
            context="查询教育相关任务"
        )
        
        assert result["success"] == True
        assert "education" in result["sql"]
        assert result["type"] == "sql"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_task_lifecycle_with_architecture(test_db, mock_api_key):
    """
    集成测试：任务生命周期（包含架构调用）
    
    创建 → 拆解 → 完成 → 查询
    """
    from unittest.mock import AsyncMock, patch
    
    orchestrator = TaskOrchestrator(test_db)
    
    # Mock 执行层响应
    mock_code_result = {
        "success": True,
        "code": "生成的代码",
        "explanation": "代码说明"
    }
    
    with patch.object(orchestrator.executor, 'execute_code_generation', new_callable=AsyncMock(return_value=mock_code_result)):
        # 1. 创建任务
        task = await orchestrator.create_task(
            title="生命周期测试",
            context=Context(category="work")
        )
        assert task.status == "pending"
        
        # 2. 拆解任务
        await orchestrator.split_task(
            task_id=task.id,
            subtasks=["子任务1", "子任务2"],
            context=Context(category="work")
        )
        
        # 获取所有任务
        all_tasks = await orchestrator.executor.get_all_tasks()
        subtasks = [t for t in all_tasks if t.parent_id == task.id]
        assert len(subtasks) == 2
        
        # 3. 完成子任务
        for subtask in subtasks:
            await orchestrator.complete_task(subtask.id)
        
        # 4. 完成父任务
        completed_task = await orchestrator.complete_task(task.id)
        assert completed_task.status == "completed"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_context_manager_integration(test_db, mock_api_key):
    """
    集成测试：上下文管理器协作
    
    学习位置/IP 映射 → 智能分类
    """
    orchestrator = TaskOrchestrator(test_db)
    
    # 学习映射
    await orchestrator.context_manager.learn_mapping(
        task_id=1,
        ip="192.168.1.100",
        location={"city": "上海", "lat": 31.23, "lon": 121.47},
        category="work"
    )
    
    # 验证映射已学习
    ip_category = await orchestrator.executor.get_category_by_location("192.168.1.100", {})
    assert ip_category == "work"
    
    # 创建新任务（应该自动分类）
    task = await orchestrator.create_task(
        title="自动分类测试",
        context=Context(ip="192.168.1.100", location={"city": "上海"})
    )
    
    assert task.category == "work"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_operations_integrity(test_db):
    """
    集成测试：数据库操作完整性
    
    测试数据库事务和回滚
    """
    orchestrator = TaskOrchestrator(test_db)
    
    # 创建任务
    task1 = await orchestrator.create_task(
        title="任务1",
        context=Context(category="work")
    )
    task2 = await orchestrator.create_task(
        title="任务2",
        context=Context(category="life")
    )
    
    # 验证任务数量
    all_tasks = await orchestrator.executor.get_all_tasks()
    assert len(all_tasks) >= 2
    
    # 删除任务
    await orchestrator.executor.delete_task(task1.id)
    
    # 验证删除后的状态
    all_tasks = await orchestrator.executor.get_all_tasks()
    remaining_tasks = [t for t in all_tasks if t.id == task1.id]
    assert len(remaining_tasks) == 0
    assert any(t.id == task2.id for t in all_tasks)
