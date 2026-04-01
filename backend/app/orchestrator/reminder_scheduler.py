from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.executor import TaskExecutor
from app.models import Task
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ReminderScheduler:
    """提醒调度器 - 编排层核心"""

    def __init__(self, executor: TaskExecutor):
        self.executor = executor
        self.scheduler = AsyncIOScheduler()
        self._started = False

    def start(self):
        """启动调度器（同步方法）"""
        if not self._started:
            self.scheduler.start()
            self._started = True
            logger.info("提醒调度器已启动")

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

        计算提醒时间：
        - 截止时间前 10 分钟
        - 截止时间前 1 小时
        - 截止时间前 1 天
        """
        due_time = task.due_time

        # 提前 10 分钟
        reminder_time_10min = due_time - timedelta(minutes=10)

        # 提前 1 小时
        reminder_time_1hour = due_time - timedelta(hours=1)

        # 提前 1 天
        reminder_time_1day = due_time - timedelta(days=1)

        now = datetime.utcnow()

        # 添加提醒任务
        if reminder_time_1day > now:
            self._add_reminder_job(
                task.id,
                reminder_time_1day,
                "时间提醒",
                f"任务【{task.title}】将在 1 天后截止",
            )

        if reminder_time_1hour > now:
            self._add_reminder_job(
                task.id,
                reminder_time_1hour,
                "时间提醒",
                f"任务【{task.title}】将在 1 小时后截止",
            )

        if reminder_time_10min > now:
            self._add_reminder_job(
                task.id,
                reminder_time_10min,
                "时间提醒",
                f"任务【{task.title}】将在 10 分钟后截止",
            )

        # 截止时间提醒
        self._add_reminder_job(
            task.id, due_time, "时间提醒", f"任务【{task.title}】已到截止时间"
        )

    def _add_reminder_job(
        self, task_id: int, run_time: datetime, reminder_type: str, message: str
    ):
        """
        添加提醒任务

        Args:
            task_id: 任务 ID
            run_time: 运行时间
            reminder_type: 提醒类型
            message: 提醒消息
        """
        job_id = f"task_{task_id}_time_{run_time.timestamp()}"

        self.scheduler.add_job(
            self._trigger_time_reminder,
            trigger="date",
            run_date=run_time,
            args=[task_id, run_time, message],
            id=job_id,
        )
        logger.info(f"安排时间提醒: task={task_id}, time={run_time}")

    async def _schedule_location_reminder(self, task: Task):
        """
        安排地点提醒

        周期检查（每 5 分钟一次）：
        - 检查用户是否进入目标区域
        - 如果进入，触发提醒
        """
        job_id = f"task_{task.id}_location_check"

        self.scheduler.add_job(
            self._check_location_reminder,
            trigger="interval",
            minutes=5,
            args=[task.id],
            id=job_id,
        )
        logger.info(f"安排位置提醒检查: task={task.id}")

    async def _trigger_time_reminder(
        self, task_id: int, reminder_time: datetime, message: str
    ):
        """
        触发时间提醒

        Args:
            task_id: 任务 ID
            reminder_time: 提醒时间
            message: 提醒消息
        """
        # 检查任务状态
        task = await self.executor.get_task(task_id)

        if not task:
            logger.warning(f"任务不存在: task_id={task_id}")
            return

        # 如果任务已完成，取消后续提醒
        if task.status == "completed":
            logger.info(f"任务已完成，取消提醒: task_id={task_id}")
            return

        # 发送提醒
        await self.executor.send_reminder(
            task=task, reminder_type="time", trigger_time=reminder_time
        )

        logger.info(f"触发时间提醒: task_id={task_id}")

    async def _check_location_reminder(self, task_id: int):
        """
        检查位置提醒

        检查用户是否进入目标区域
        """
        # 获取任务
        task = await self.executor.get_task(task_id)

        if not task:
            logger.warning(f"任务不存在: task_id={task_id}")
            return

        # 如果任务已完成，停止检查
        if task.status == "completed":
            logger.info(f"任务已完成，停止位置检查: task_id={task_id}")
            # 移除定时任务
            try:
                self.scheduler.remove_job(f"task_{task_id}_location_check")
            except Exception:
                pass
            return

        # 简化实现：这里需要获取用户当前位置
        # 实际应该从 API 请求中获取，这里暂时跳过
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
