from app.executor import TaskExecutor
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Context:
    """上下文数据类"""

    def __init__(
        self,
        ip: str,
        location: Optional[Dict[str, Any]] = None,
        category: Optional[str] = None,
        mode: str = "auto",
    ):
        self.ip = ip
        self.location = location
        self.category = category
        self.mode = mode


class ContextManager:
    """上下文管理器 - 编排层核心"""

    def __init__(self, executor: TaskExecutor):
        self.executor = executor
        self.current_mode = "auto"  # auto | manual
        self.cache = {}  # 缓存最近的检测结果

    async def get_current_context(self, client_ip: str) -> Context:
        """
        获取当前上下文

        编排层职责：
        - 自动检测IP/位置
        - 判断当前应该是哪种模式
        - 支持手动覆盖
        """
        # 1. 检查是否手动指定
        if self.current_mode == "manual":
            return Context(
                ip=client_ip, mode="manual", category=self._get_manual_category()
            )

        # 2. 自动检测
        # 尝试从缓存获取
        if client_ip in self.cache:
            return self.cache[client_ip]

        # 获取地理位置
        user_location = await self.executor.external_services.query_location(client_ip)

        # 查询IP/位置映射
        category = await self.executor.get_category_by_location(
            client_ip, user_location
        )

        # 创建上下文
        context = Context(
            ip=client_ip, location=user_location, category=category, mode="auto"
        )

        # 缓存结果
        self.cache[client_ip] = context

        logger.info(f"获取当前上下文: ip={client_ip}, category={category}")
        return context

    def set_manual_mode(self, category: str):
        """设置手动模式"""
        self.current_mode = "manual"
        self._manual_category = category
        logger.info(f"设置手动模式: category={category}")

    def set_auto_mode(self):
        """设置自动模式"""
        self.current_mode = "auto"
        logger.info("切换到自动模式")

    def _get_manual_category(self) -> Optional[str]:
        """获取手动指定的分类"""
        return getattr(self, "_manual_category", None)

    async def learn_mapping(
        self, task_id: int, ip: str, location: Dict[str, Any], category: str
    ):
        """
        自动学习IP/位置映射

        编排层职责：
        - 记录任务创建时的IP/位置
        - 统计任务分类分布
        - 自动生成映射规则
        """
        # 记录关联关系
        await self.executor.record_task_location(
            task_id=task_id, ip=ip, location=location, category=category
        )

        # 如果数据足够，自动生成规则
        await self._auto_generate_rules()

    async def _auto_generate_rules(self):
        """
        自动生成IP/位置映射规则

        算法：
        1. 统计每个IP/位置的任务分类分布
        2. 如果某个分类占比>80%，自动生成规则
        3. 标记为auto=True
        """
        # 查询统计数据
        stats = await self.executor.get_location_statistics()

        # 按IP分组统计
        ip_stats: Dict[str, Dict[str, int]] = {}
        for stat in stats:
            ip = stat["ip"]
            category = stat["category"]
            count = stat["task_count"]

            if ip not in ip_stats:
                ip_stats[ip] = {}
            if category not in ip_stats[ip]:
                ip_stats[ip][category] = 0

            ip_stats[ip][category] += count

        # 生成规则
        for ip, category_counts in ip_stats.items():
            total = sum(category_counts.values())
            for category, count in category_counts.items():
                ratio = count / total

                # 如果某个分类占比>80%，自动生成规则
                if ratio > 0.8:
                    await self.executor.upsert_ip_mapping(
                        ip_pattern=ip, category=category, auto=True
                    )
                    logger.info(
                        f"自动生成IP映射规则: {ip} -> {category} (占比{ratio:.2%})"
                    )

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        logger.info("清空上下文缓存")
