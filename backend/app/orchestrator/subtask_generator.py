"""AI 子任务生成器 - 调用外部 AI API 自动生成子任务"""

import json
import logging
from typing import Any, Dict, List, Optional

from app.llm.tasks.subtask import subtask_async

logger = logging.getLogger(__name__)


_TEST_TITLE_PATTERNS = [
    "e2e",
    "e2e 测试",
    "e2e测试",
    "测试任务",
    "mock",
]


def _is_test_title(title: str) -> bool:
    """检查任务标题是否疑似测试数据"""
    title_lower = title.lower()
    for pattern in _TEST_TITLE_PATTERNS:
        if pattern in title_lower:
            return True
    return False


def _is_subtask_of_test(task: Any, tasks_map: Dict[int, Any]) -> bool:
    """检查任务是否是测试任务的子任务"""
    # 向上遍历父任务链
    current = task
    while current.parent_id and current.parent_id in tasks_map:
        parent = tasks_map[current.parent_id]
        if _is_test_title(parent.title):
            return True
        current = parent
    return False


async def generate_subtasks(title: str, description: Optional[str] = None) -> List[str]:
    """
    调用 AI API 根据任务标题和描述生成子任务列表

    Args:
        title: 任务标题
        description: 任务描述（可选）

    Returns:
        子任务标题列表，失败时返回空列表
    """
    # 跳过测试相关的任务，不生成 AI 子任务
    if _is_test_title(title):
        logger.info(f"跳过测试任务自动生成子任务: {title}")
        return []

    # 构建输入内容
    content = f"任务：{title}"
    if description:
        content += f"\n描述：{description}"

    # 调用 LLM 模块
    try:
        result = await subtask_async(content)
        response = json.loads(result)

        if not response.get("ok"):
            logger.info(f"AI 子任务生成未配置或失败: {response.get('error')}")
            return []

        data = response.get("data")
        if isinstance(data, list):
            return [s.strip() for s in data if isinstance(s, str)]
        else:
            logger.warning(f"AI 返回数据格式不是列表: {type(data)}")
            return []

    except json.JSONDecodeError as e:
        logger.warning(f"AI 子任务响应解析失败: {e}")
        return []
    except Exception as e:
        logger.warning(f"AI 子任务生成异常（不影响主任务创建）: {e}")
        return []


def _parse_subtasks(content: str) -> List[str]:
    """
    从 AI 返回内容中解析子任务列表（备用解析方法）

    保留用于兼容性或备用解析场景
    """
    # 尝试直接解析 JSON
    try:
        result = json.loads(content)
        if isinstance(result, list):
            return [str(item).strip() for item in result if str(item).strip()]
    except json.JSONDecodeError:
        pass

    # 尝试提取 JSON 数组
    import re

    match = re.search(r"\[.*\]", content, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, list):
                return [str(item).strip() for item in result if str(item).strip()]
        except json.JSONDecodeError:
            pass

    # 最后尝试按行分割
    lines = [
        line.strip().lstrip("0123456789.-) ")
        for line in content.split("\n")
        if line.strip()
    ]
    return lines if lines else []
