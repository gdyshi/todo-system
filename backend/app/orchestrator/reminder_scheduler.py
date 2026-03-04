from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.executor import TaskExecutor
from app.models import Task
from datetime import datetime, timedelta
from typing import List
import logging

logger = logging.getLogger(__name__)


class ReminderScheduler:
    """提醒调度器 - 编排层核心"""

    def __init__(self, executor: TaskExecutor):
        self.executor = executor
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

    async def schedule_reminders(self, task: Task):
        """
        为任务安排提醒

        编排层职责：
        - 解析提醒时间/地点
        - 安排定时任务
        - 设置地点监听
        """
        # 1. 时间提醒
        if task.due_time:
            await self._schedule_time_reminder(task)

        # 2. 地点提醒
        if task.location:
            await self._schedule_location_reminder(task)

    async def _schedule_time_reminder(self, task: Task):
        """
        安排时间提醒

        提醒规则：
        - 提前1小时
        - 提前1天
        - 截止时间
        """
        if not task.due_time:
            return

        reminders = self._calculate_time_reminders(task.due_time)

        for reminder_time in reminders:
            if reminder_time > datetime.utcnow():
                self.scheduler.add_job(
                    func=self._trigger_time_reminder,
                    trigger="date",
                    run_date=reminder_time,
                    args=[task.id, reminder_time],
                    id=f"task_{task.id}_time_{reminder_time.timestamp()}"
                )
                logger.info(f"安排时间提醒: task={task.id}, time={reminder_time}")

    def _calculate_time_reminders(self, due_time: datetime) -> List[datetime]:
        """计算时间提醒点"""
        reminders = []

        # 截止时间
        reminders.append(due_time)

        # 提前1小时
        if due_time - timedelta(hours=1) > datetime.utcnow():
            reminders.append(due_time - timedelta(hours=1))

        # 提前1天
        if due_time - timedelta(days=1) > datetime.utcnow():
            reminders.append(due_time - timedelta(days=1))

        return reminders

    async def _schedule_location_reminder(self, task: Task):
        """
        安排地点提醒

        提醒规则：
        - 定期检查用户位置
        - 进入指定区域时提醒
        """
        # 简化实现：每5分钟检查一次
        self.scheduler.add_job(
            func=self._check_location_reminder,
            trigger="interval",
            minutes=5,
            args=[task.id],
            id=f"task_{task.id}_location_check"
        )
        logger.info(f"安排位置提醒检查: task={task.id}")

    async def _trigger_time_reminder(self, task_id: int, reminder_time: datetime):
        """
        触发时间提醒

        编排层职责：
        - 获取任务详情
        - 判断是否还需要提醒（可能已经完成）
        - 选择通知方式（Telegram/邮件）
        """
        task = await self.executor.get_task(task_id)

        # 检查任务状态
        if not task or task.status == "completed":
            logger.info(f"任务已完成，取消提醒: task_id={task_id}")
            return

        # 下达发送指令
        await self.executor.send_reminder(
            task=task,
            type="time",
            trigger_time=reminder_time
        )

        logger.info(f"触发时间提醒: task_id={task_id}")

    async def _check_location_reminder(self, task_id: int):
        """
        检查位置提醒

        编排层职责：
        - 判断是否进入/离开目标区域
        - 触发提醒
        """
        task = await self.executor.get_task(task_id)

        # 检查任务状态
        if not task or task.status == "completed" or not task.location:
            return

        # 简化实现：这里需要获取用户当前位置
        # 实际应该从API请求中获取，这里暂时跳过
        logger.debug(f"检查位置提醒: task_id={task_id}")

    async def cancel_reminders(self, task_id: int):
        """取消任务的所有提醒"""
        # 取消所有相关job
        jobs = self.scheduler.get_jobs()
        for job in jobs:
            if f"task_{task_id}_" in job.id:
                self.scheduler.remove_job(job.id)
                logger.info(f"取消提醒: job_id={job.id}")

    async def check_next_reminders(self, task: Task):
        """
        检查并触发后续提醒

        完成任务时检查是否有相关任务的提醒需要触发
        """
        # 简化实现：这里可以检查父任务的子任务是否都完成
        # 如果都完成，触发父任务的提醒
        pass

    def shutdown(self):
        """关闭调度器"""
        self.scheduler.shutdown()
        logger.info("提醒调度器已关闭")
