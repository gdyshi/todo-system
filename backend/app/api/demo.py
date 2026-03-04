"""测试双层架构的 API 端点"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.tasks import get_db
from app.orchestrator.task_orchestrator import TaskOrchestrator
from app.models import Task
from typing import Optional

router = APIRouter(prefix="/demo", tags=["demo"])


class CodeGenerationRequest(BaseModel):
    """代码生成请求"""
    task_id: Optional[int] = None
    operation: str = "query"  # query, create_api, analyze
    custom_prompt: Optional[str] = None


class CodeGenerationResponse(BaseModel):
    """代码生成响应"""
    success: bool
    operation: str
    code: Optional[str] = None
    explanation: Optional[str] = None
    error: Optional[str] = None


@router.post("/generate-code", response_model=CodeGenerationResponse)
async def generate_code(
    request: CodeGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    测试双层架构的代码生成

    流程：
    1. 编排层接收请求
    2. 生成精确的 prompt
    3. 调用执行层（GLM Coding Lite API）
    4. 返回结果
    """
    orchestrator = TaskOrchestrator(db)

    # 如果有自定义 prompt，直接使用
    if request.custom_prompt:
        result = await orchestrator.executor.execute_code_generation(
            task_description=request.custom_prompt,
            task_type=orchestrator._determine_task_type(request.operation)
        )
        operation = request.operation
    else:
        # 如果有 task_id，使用任务上下文
        if request.task_id:
            task = await orchestrator.executor.get_task(request.task_id)
            if not task:
                raise HTTPException(status_code=404, detail="任务不存在")

            result = await orchestrator.generate_and_execute_code(
                task=task,
                operation=request.operation
            )
            operation = f"{request.operation} (task #{task.id})"
        else:
            # 使用默认任务
            task = Task(
                id=0,
                title="测试任务",
                category="demo",
                description="这是一个演示双层架构的测试任务",
                status="pending"
            )
            result = await orchestrator.generate_and_execute_code(
                task=task,
                operation=request.operation
            )
            operation = f"{request.operation} (demo)"

    return CodeGenerationResponse(
        success=result["success"],
        operation=operation,
        code=result.get("code"),
        explanation=result.get("explanation"),
        error=result.get("error")
    )


@router.get("/architecture")
async def get_architecture_info():
    """
    获取架构信息

    解释当前的双层架构设计
    """
    return {
        "architecture": "双层架构",
        "layers": {
            "orchestration": {
                "name": "TaskOrchestrator",
                "description": "编排层 - 持有业务上下文，生成精确的 prompt",
                "responsibilities": [
                    "理解用户需求",
                    "持有业务上下文（任务分类、历史记录）",
                    "生成精确的 prompt",
                    "监控执行进度，失败后调整 prompt 重试",
                    "调用执行层"
                ],
                "does_not": [
                    "直接编写代码",
                    "访问生产数据库（只读权限）",
                    "调用外部 API（除了 GLM Coding Lite）"
                ]
            },
            "execution": {
                "name": "CodeExecutor (GLM Coding Lite)",
                "description": "执行层 - 专注于代码生成和执行",
                "responsibilities": [
                    "接收编排层的 prompt",
                    "调用 GLM Coding Lite API 生成代码",
                    "返回生成的代码和解释",
                    "专注于技术实现"
                ],
                "does_not": [
                    "持有业务上下文",
                    "访问生产数据库",
                    "理解业务逻辑"
                ]
            }
        },
        "flow": [
            "用户 → 编排层（理解需求）",
            "编排层 → 生成 prompt",
            "编排层 → 执行层（调用 GLM API）",
            "执行层 → GLM Coding Lite（生成代码）",
            "执行层 → 编排层（返回结果）",
            "编排层 → 用户（处理结果）"
        ],
        "based_on": "OpenClaw + Claude Code 双层架构",
        "adaptation": "使用 GLM Coding Lite 替代 Claude Code"
    }
