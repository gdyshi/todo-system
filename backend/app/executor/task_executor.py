from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Task, IPMapping, TaskLocation
from app.executor.external_services import external_services
from app.executor.code_executor import CodeExecutor
from app.config import settings
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class TaskExecutor:
    """任务执行器 - 执行层核心"""

    def __init__(self, db: Session):
        self.db = db
        # 初始化代码执行器（调用 GLM Coding Lite API）
        self.code_executor = CodeExecutor(
            api_key=settings.glm_api_key, model=settings.glm_model
        )
        # 添加 external_services 作为属性
        self.external_services = external_services

    async def create_task(
        self,
        title: str,
        category: str,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
        priority: int = 0,
        due_time: Optional[datetime] = None,
        location: Optional[str] = None,
        **kwargs,
    ) -> Task:
        """创建任务"""
        task = Task(
            title=title,
            description=description,
            category=category,
            parent_id=parent_id,
            priority=priority,
            due_time=due_time,
            location=location,
            status="pending",
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        logger.info(f"创建任务成功: {task.id} - {task.title}")
        return task

    async def get_task(self, task_id: int) -> Optional[Task]:
        """获取任务"""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        return task

    async def get_all_tasks(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        parent_id: Optional[int] = None,
    ) -> List[Task]:
        """获取所有任务"""
        query = self.db.query(Task)
        if category:
            query = query.filter(Task.category == category)
        if status:
            query = query.filter(Task.status == status)
        if parent_id is not None:
            query = query.filter(Task.parent_id == parent_id)
        else:
            query = query.filter(Task.parent_id.is_(None))  # 默认只返回顶级任务

        tasks = query.order_by(Task.priority.desc(), Task.created_at.desc()).all()
        return tasks

    async def update_task(self, task_id: int, **kwargs) -> Optional[Task]:
        """更新任务"""
        task = await self.get_task(task_id)
        if not task:
            return None

        for key, value in kwargs.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)

        task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(task)
        logger.info(f"更新任务成功: {task_id}")
        return task

    async def complete_task(self, task_id: int) -> Optional[Task]:
        """完成任务"""
        task = await self.get_task(task_id)
        if not task:
            return None

        # 检查是否有未完成的子任务
        incomplete_subtasks = (
            self.db.query(Task)
            .filter(and_(Task.parent_id == task_id, Task.status != "completed"))
            .count()
        )

        if incomplete_subtasks > 0:
            raise ValueError("请先完成所有子任务")

        task.status = "completed"
        task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(task)
        logger.info(f"完成任务成功: {task_id}")
        return task

    async def delete_task(self, task_id: int) -> bool:
        """删除任务（级联删除子任务）"""
        task = await self.get_task(task_id)
        if not task:
            return False

        self.db.delete(task)
        self.db.commit()
        logger.info(f"删除任务成功: {task_id}")
        return True

    async def get_category_by_location(
        self, ip: str, location: Dict[str, Any]
    ) -> Optional[str]:
        """根据IP/位置获取分类"""
        # 先查找IP映射
        mapping = self.db.query(IPMapping).filter(IPMapping.ip_pattern == ip).first()

        if mapping:
            return mapping.category

        # 如果没有IP映射，查找位置映射
        # 这里简化处理，实际可以根据经纬度范围匹配
        # 暂时返回默认值
        return None

    async def record_task_location(
        self, task_id: int, ip: str, location: Dict[str, Any], category: str
    ):
        """记录任务位置"""
        task_location = TaskLocation(
            task_id=task_id,
            ip=ip,
            location=json.dumps(location) if location else None,
            category=category,
        )
        self.db.add(task_location)
        self.db.commit()
        logger.info(f"记录任务位置成功: task_id={task_id}, ip={ip}")

    async def get_location_statistics(self) -> List[Dict[str, Any]]:
        """获取位置统计"""
        # 统计每个IP/位置的任务分类分布
        stats = (
            self.db.query(
                TaskLocation.ip, TaskLocation.category, Task.id.label("task_count")
            )
            .join(Task, TaskLocation.task_id == Task.id)
            .group_by(TaskLocation.ip, TaskLocation.category)
            .all()
        )

        results = []
        for stat in stats:
            results.append(
                {
                    "ip": stat.ip,
                    "category": stat.category,
                    "task_count": stat.task_count,
                }
            )

        return results

    async def upsert_ip_mapping(
        self,
        ip_pattern: str,
        category: str,
        auto: bool = True,
        manual_override: bool = False,
    ):
        """创建或更新IP映射"""
        mapping = (
            self.db.query(IPMapping).filter(IPMapping.ip_pattern == ip_pattern).first()
        )

        if mapping:
            mapping.category = category
            mapping.auto = auto
            mapping.manual_override = manual_override
            mapping.updated_at = datetime.utcnow()
        else:
            mapping = IPMapping(
                ip_pattern=ip_pattern,
                category=category,
                auto=auto,
                manual_override=manual_override,
            )
            self.db.add(mapping)

        self.db.commit()
        logger.info(f"创建/更新IP映射成功: {ip_pattern} -> {category}")

    async def get_all_ip_mappings(self) -> List[IPMapping]:
        """获取所有IP映射"""
        mappings = (
            self.db.query(IPMapping)
            .order_by(
                IPMapping.auto.desc(), IPMapping.created_at.desc()  # 自动生成的排前面
            )
            .all()
        )
        return mappings

    async def delete_ip_mapping(self, mapping_id: int) -> bool:
        """删除IP映射"""
        mapping = self.db.query(IPMapping).filter(IPMapping.id == mapping_id).first()
        if not mapping:
            return False

        self.db.delete(mapping)
        self.db.commit()
        logger.info(f"删除IP映射成功: {mapping_id}")
        return True

    async def send_reminder(self, task: Task, reminder_type: str, **kwargs):
        """发送提醒"""
        if reminder_type == "time":
            message = f"⏰ 时间提醒\n\n任务：{task.title}\n分类：{task.category}\n状态：{task.status}"
            if task.due_time:
                message += f"\n截止时间：{task.due_time.strftime('%Y-%m-%d %H:%M')}"

            # 发送Telegram
            await external_services.send_telegram_message(message)

            # 邮件功能已移除

        elif reminder_type == "location":
            current_location = kwargs.get("current_location", {})
            message = f"📍 地点提醒\n\n任务：{task.title}\n分类：{task.category}\n状态：{task.status}"
            if current_location:
                message += f"\n当前位置：{current_location.get('city', 'Unknown')}"

            # 发送Telegram
            await external_services.send_telegram_message(message)

            # 邮件功能已移除

        # 标记已发送
        task.reminder_sent = True
        self.db.commit()

    async def execute_code_generation(
        self,
        task_description: str,
        task_type: str = "general",
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        执行代码生成任务

        编排层调用此方法，传入任务描述和上下文
        执行层通过 GLM Coding Lite API 生成代码

        这是双层架构的核心：编排层不直接写代码，而是通过执行层调用 GLM API

        Args:
            task_description: 任务描述（由编排层生成的精确 prompt）
            task_type: 任务类型（general, sql, api 等）
            context: 额外的上下文信息

        Returns:
            执行结果字典
        """
        logger.info(
            f"执行代码生成任务: type={task_type}, description={task_description[:100]}..."
        )

        if task_type == "sql":
            return await self.code_executor.execute_sql_query(
                query=task_description, description=context or "数据库查询任务"
            )
        elif task_type == "api":
            return await self.code_executor.generate_api_endpoint(
                endpoint_description=task_description, context=context
            )
        else:
            return await self.code_executor.execute_code_task(
                prompt=task_description, context=context
            )
