from sqlalchemy.orm import Session
from app.executor import TaskExecutor
from app.models import Task
from app.orchestrator.context_manager import ContextManager, Context
from app.orchestrator.subtask_generator import generate_subtasks
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TaskOrchestrator:
    """
    任务编排器 - 编排层核心

    编排层职责：
    - 理解用户意图和需求
    - 持有业务上下文（任务分类、历史记录等）
    - 生成精确的 prompt
    - 调用执行层（GLM Coding Lite）完成任务
    - 监控执行进度，失败后调整 prompt 重试
    """

    def __init__(
        self,
        db: Session,
        context_manager: ContextManager = None,
        scheduler=None,  # 接收外部 scheduler（全局单例）
    ):
        self.executor = TaskExecutor(db)
        self.context_manager = context_manager or ContextManager(self.executor)
        # 使用传入的 scheduler（全局单例）
        self.reminder_scheduler = scheduler

    async def create_task(
        self,
        title: str,
        context: Context,
        description: Optional[str] = None,
        subtasks: Optional[List[str]] = None,
        priority: int = 0,
        due_time: Optional[datetime] = None,
        location: Optional[str] = None,
    ) -> Task:
        """
        创建任务

        编排层职责：
        - 理解用户意图
        - 智能分类
        - 拆分子任务
        - 安排提醒
        """
        # 1. 解析用户输入
        task_info = self._parse_user_input(title)

        # 2. 智能分类（可手动调整）
        if context.category:
            category = context.category
        else:
            category = self._classify_task(task_info, context)

        # 兜底：确保 category 不为空（数据库 NOT NULL 约束）
        if not category:
            category = "life"

        # 3. 创建主任务
        task = await self.executor.create_task(
            title=task_info["title"],
            category=category,
            description=description or task_info["description"],
            priority=priority,
            due_time=due_time,
            location=location,
        )

        # 4. 学习IP/位置映射
        await self.context_manager.learn_mapping(
            task_id=task.id, ip=context.ip, location=context.location, category=category
        )

        # 5. 如果需要拆分子任务
        if subtasks:
            for subtask_title in subtasks:
                await self._create_subtask(task.id, subtask_title, category)
        else:
            # 自动生成子任务（AI）
            auto_subtasks = await generate_subtasks(
                task_info["title"], description or task_info.get("description")
            )
            for subtask_title in auto_subtasks:
                await self._create_subtask(task.id, subtask_title, category)

        # 6. 安排提醒
        await self.reminder_scheduler.schedule_reminders(task)

        logger.info(f"编排器创建任务成功: {task.id} - {task.title}")
        return task

    async def _create_subtask(self, parent_id: int, title: str, category: str) -> Task:
        """创建子任务"""
        subtask = await self.executor.create_task(
            title=title, category=category, parent_id=parent_id
        )
        logger.info(f"创建子任务成功: {subtask.id} - {subtask.title}")
        return subtask

    async def split_task(
        self, task_id: int, subtasks: List[str], context: Context
    ) -> List[Task]:
        """
        拆解任务为子任务

        编排层职责：
        - 理解拆解意图
        - 生成合理的子任务
        - 维护任务层级关系
        """
        # 获取父任务
        parent_task = await self.executor.get_task(task_id)
        if not parent_task:
            raise ValueError(f"任务不存在: {task_id}")

        # 创建子任务
        subtask_objs = []
        for subtask_title in subtasks:
            subtask = await self._create_subtask(
                task_id, subtask_title, parent_task.category
            )
            subtask_objs.append(subtask)

        logger.info(f"拆解任务成功: {task_id}, 子任务数: {len(subtask_objs)}")
        return subtask_objs

    async def complete_task(self, task_id: int) -> Task | None:
        """
        完成任务

        编排层职责：
        - 检查是否所有子任务都完成
        - 更新父任务状态
        - 触发后续提醒
        """
        # 下达完成指令
        task = await self.executor.complete_task(task_id)

        # 取消提醒
        await self.reminder_scheduler.cancel_reminders(task_id)

        # 触发后续提醒
        await self.reminder_scheduler.check_next_reminders(task)

        logger.info(f"完成任务成功: {task_id}")
        return task

    def _parse_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        解析用户输入

        编排层职责：
        - 识别任务类型
        - 提取关键信息
        """
        # 简化实现：返回基本信息
        return {"title": user_input, "description": None}

    def _classify_task(self, task_info: Dict[str, Any], context: Context) -> str:
        """
        智能分类任务

        编排层职责：
        - 根据上下文判断
        - 根据任务内容判断
        """
        # 优先使用上下文中的分类
        if context.category:
            return context.category

        # 根据任务内容判断
        title = task_info["title"].lower()

        # 工作相关关键词（优先级最高，优先匹配）
        work_keywords = [
            "工作",
            "项目",
            "报告",
            "会议",
            "文档",
            "代码",
            "bug",
            "功能",
            "客户",
            "需求",
            "周报",
            "日报",
            "方案",
            "策划",
            "招标",
            "投标",
        ]
        if any(keyword in title for keyword in work_keywords):
            return "work"

        # 教育相关关键词
        education_keywords = [
            "学习",
            "课程",
            "考试",
            "作业",
            "论文",
            "阅读",
            "研究",
            "笔记",
        ]
        if any(keyword in title for keyword in education_keywords):
            return "education"

        # 默认为生活相关
        return "life"

    async def get_context(self, client_ip: str) -> Context:
        """获取当前上下文"""
        return await self.context_manager.get_current_context(client_ip)

    def set_manual_mode(self, category: str):
        """设置手动模式"""
        self.context_manager.set_manual_mode(category)

    def set_auto_mode(self):
        """设置自动模式"""
        self.context_manager.set_auto_mode()

    async def generate_and_execute_code(
        self, task: Task, operation: str, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成 prompt 并调用执行层

        这是双层架构的核心流程：
        1. 编排层根据任务和操作生成精确的 prompt
        2. 调用执行层（通过 GLM Coding Lite API）
        3. 执行层返回结果
        4. 编排层处理结果

        Args:
            task: 任务对象
            operation: 要执行的操作（如：生成查询、创建 API、分析数据等）
            context: 额外的上下文信息

        Returns:
            执行结果
        """
        # 编排层生成 prompt
        prompt = self._generate_prompt_for_operation(task, operation, context)

        logger.info(f"编排层生成 prompt: {prompt[:200]}...")

        # 调用执行层（GLM Coding Lite）
        task_type = self._determine_task_type(operation)
        result = await self.executor.execute_code_generation(
            task_description=prompt, task_type=task_type, context=context
        )

        # 如果失败，编排层调整 prompt 重试
        if not result["success"]:
            logger.warning("执行层首次调用失败，尝试调整 prompt")
            adjusted_prompt = self._adjust_prompt_on_failure(
                prompt, result.get("error") or ""
            )
            result = await self.executor.execute_code_generation(
                task_description=adjusted_prompt, task_type=task_type, context=context
            )

        return result

    def _generate_prompt_for_operation(
        self, task: Task, operation: str, context: Optional[str] = None
    ) -> str:
        """
        为操作生成精确的 prompt

        这是编排层的核心能力：根据业务上下文生成精确的 prompt

        Args:
            task: 任务对象
            operation: 操作类型
            context: 额外上下文

        Returns:
            精确的 prompt
        """
        # 基础信息
        prompt_parts = [
            f"任务标题：{task.title}",
            f"任务分类：{task.category}",
        ]

        if task.description:
            prompt_parts.append(f"任务描述：{task.description}")

        if task.due_time:
            prompt_parts.append(f"截止时间：{task.due_time.strftime('%Y-%m-%d %H:%M')}")

        # 添加上下文
        if context:
            prompt_parts.append(f"\n上下文信息：\n{context}")

        # 根据操作类型添加特定指令
        operation_prompts = {
            "query": "生成一个 SQLAlchemy 查询来获取相关任务数据",
            "create_api": "创建一个 FastAPI 端点来处理这个任务",
            "analyze": "分析任务数据并生成报告",
            "default": "根据上述信息完成相关代码任务",
        }

        prompt_parts.append(
            f"\n操作：{operation_prompts.get(operation, operation_prompts['default'])}"
        )

        return "\n".join(prompt_parts)

    def _determine_task_type(self, operation: str) -> str:
        """确定任务类型"""
        operation_lower = operation.lower()

        if (
            "sql" in operation_lower
            or "query" in operation_lower
            or "数据库" in operation
        ):
            return "sql"
        elif (
            "api" in operation_lower
            or "endpoint" in operation_lower
            or "接口" in operation
        ):
            return "api"
        else:
            return "general"

    def _adjust_prompt_on_failure(self, original_prompt: str, error: str) -> str:
        """
        失败后调整 prompt

        类似原文中的改进版 Ralph Loop，不是简单重试，而是分析失败原因并调整

        Args:
            original_prompt: 原始 prompt
            error: 错误信息

        Returns:
            调整后的 prompt
        """
        # 简化实现：根据错误类型调整
        adjusted_prompt = f"""上次执行失败，错误信息：{error}

请根据上述错误重新生成代码，确保：
1. 修复错误
2. 保持原有功能
3. 使用更简单直接的方法

原始任务：
{original_prompt}"""

        return adjusted_prompt
