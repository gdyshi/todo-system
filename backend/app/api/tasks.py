from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.models import get_db, Task, IPMapping
from app.orchestrator import TaskOrchestrator

router = APIRouter()


# Pydantic模型
class TaskCreate(BaseModel):
    title: str = Field(..., description="任务标题")
    description: Optional[str] = Field(None, description="任务描述")
    subtasks: Optional[List[str]] = Field(None, description="子任务列表")
    priority: int = Field(0, description="优先级 0-9")
    due_time: Optional[datetime] = Field(None, description="截止时间")
    location: Optional[str] = Field(None, description="地点提醒坐标（JSON格式）")


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    due_time: Optional[datetime] = None
    location: Optional[str] = None


class TaskSplit(BaseModel):
    subtasks: List[str] = Field(..., description="子任务列表")


class CategoryMode(BaseModel):
    mode: str = Field(..., description="模式：auto|manual")
    category: Optional[str] = Field(None, description="手动模式下指定的分类")


# 依赖注入
def get_orchestrator(db: Session = Depends(get_db)) -> TaskOrchestrator:
    """获取编排器"""
    import os
    from app.main import get_context_manager

    # 在测试环境中禁用 scheduler
    auto_start_scheduler = os.getenv("PYTEST_CURRENT_TEST") is None
    context_manager = get_context_manager()

    return TaskOrchestrator(
        db, auto_start_scheduler=auto_start_scheduler, context_manager=context_manager
    )


# API端点
@router.get("/tasks", response_model=List[dict])
async def get_tasks(
    category: Optional[str] = None,
    status: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    orchestrator: TaskOrchestrator = Depends(get_orchestrator),
):
    """获取任务列表"""
    executor = orchestrator.executor
    tasks = await executor.get_all_tasks(category=category, status=status)
    return [task.to_dict() for task in tasks]


@router.get("/tasks/{task_id}", response_model=dict)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """获取单个任务"""
    executor = TaskOrchestrator(db).executor
    task = await executor.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task.to_dict()


@router.post("/tasks", response_model=dict)
async def create_task(
    task_data: TaskCreate,
    request: Request,
    db: Session = Depends(get_db),
    orchestrator: TaskOrchestrator = Depends(get_orchestrator),
):
    """创建任务"""
    # 获取客户端IP
    client_ip = request.client.host if request.client else "127.0.0.1"

    # 获取上下文
    context = await orchestrator.get_context(client_ip)

    # 创建任务
    task = await orchestrator.create_task(
        title=task_data.title,
        context=context,
        description=task_data.description,
        subtasks=task_data.subtasks,
        priority=task_data.priority,
        due_time=task_data.due_time,
        location=task_data.location,
    )

    return task.to_dict()


@router.put("/tasks/{task_id}", response_model=dict)
async def update_task(
    task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db)
):
    """更新任务"""
    executor = TaskOrchestrator(db).executor

    update_data = task_data.dict(exclude_unset=True)
    task = await executor.update_task(task_id, **update_data)

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return task.to_dict()


@router.post("/tasks/{task_id}/complete", response_model=dict)
async def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    orchestrator: TaskOrchestrator = Depends(get_orchestrator),
):
    """完成任务"""
    try:
        task = await orchestrator.complete_task(task_id)
        return task.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tasks/{task_id}/split", response_model=List[dict])
async def split_task(
    task_id: int,
    split_data: TaskSplit,
    request: Request,
    db: Session = Depends(get_db),
    orchestrator: TaskOrchestrator = Depends(get_orchestrator),
):
    """拆解任务为子任务"""
    # 获取客户端IP
    client_ip = request.client.host if request.client else "127.0.0.1"

    # 获取上下文
    context = await orchestrator.get_context(client_ip)

    # 拆解任务
    subtasks = await orchestrator.split_task(
        task_id=task_id, subtasks=split_data.subtasks, context=context
    )

    return [subtask.to_dict() for subtask in subtasks]


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """删除任务"""
    executor = TaskOrchestrator(db).executor
    success = await executor.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"message": "任务删除成功"}


# 分类模式管理
@router.post("/mode")
async def set_mode(
    mode_data: CategoryMode, orchestrator: TaskOrchestrator = Depends(get_orchestrator)
):
    """设置分类模式"""
    if mode_data.mode == "manual":
        if not mode_data.category:
            raise HTTPException(status_code=400, detail="手动模式需要指定分类")
        orchestrator.set_manual_mode(mode_data.category)
    elif mode_data.mode == "auto":
        orchestrator.set_auto_mode()
    else:
        raise HTTPException(status_code=400, detail="无效的模式")

    return {"message": f"模式已设置为: {mode_data.mode}"}


@router.get("/mode")
async def get_mode(
    request: Request, orchestrator: TaskOrchestrator = Depends(get_orchestrator)
):
    """获取当前模式"""
    client_ip = request.client.host if request.client else "127.0.0.1"
    context = await orchestrator.get_context(client_ip)

    return {
        "mode": context.mode,
        "category": context.category,
        "ip": context.ip,
        "location": context.location,
    }


# IP映射管理
@router.get("/ip-mappings", response_model=List[dict])
async def get_ip_mappings(db: Session = Depends(get_db)):
    """获取所有IP映射"""
    executor = TaskOrchestrator(db).executor
    mappings = await executor.get_all_ip_mappings()
    return [mapping.to_dict() for mapping in mappings]


@router.delete("/ip-mappings/{mapping_id}")
async def delete_ip_mapping(mapping_id: int, db: Session = Depends(get_db)):
    """删除IP映射"""
    executor = TaskOrchestrator(db).executor
    success = await executor.delete_ip_mapping(mapping_id)
    if not success:
        raise HTTPException(status_code=404, detail="IP映射不存在")
    return {"message": "IP映射删除成功"}


# 统计信息
@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """获取统计信息"""
    executor = TaskOrchestrator(db).executor

    # 获取所有任务
    all_tasks = await executor.get_all_tasks()

    # 统计
    total = len(all_tasks)
    completed = sum(1 for task in all_tasks if task.status == "completed")
    pending = sum(1 for task in all_tasks if task.status == "pending")
    in_progress = sum(1 for task in all_tasks if task.status == "in_progress")

    # 按分类统计
    by_category = {}
    for task in all_tasks:
        cat = task.category
        if cat not in by_category:
            by_category[cat] = {"total": 0, "completed": 0}
        by_category[cat]["total"] += 1
        if task.status == "completed":
            by_category[cat]["completed"] += 1

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "in_progress": in_progress,
        "by_category": by_category,
    }
