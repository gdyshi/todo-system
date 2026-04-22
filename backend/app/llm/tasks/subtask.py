"""子任务生成 - 调用 LLM 拆解任务"""

import asyncio
import logging

from app.llm.core import chat

logger = logging.getLogger(__name__)


async def subtask_async(content: str) -> str:
    """
    调用 LLM 生成子任务列表（异步版本，用于内部调用）

    Args:
        content: 任务内容

    Returns:
        JSON 字符串格式的 LLMResponse
    """
    response = await chat("subtask", content)
    return response.to_json_string()


def subtask(content: str) -> str:
    """
    调用 LLM 生成子任务列表

    Args:
        content: 任务内容

    Returns:
        JSON 字符串格式的 LLMResponse
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        response = loop.run_until_complete(chat("subtask", content))
    finally:
        loop.close()

    return response.to_json_string()
