"""任务分类 - 调用 LLM 判断任务分类"""

import asyncio
import logging

from app.llm.core import chat

logger = logging.getLogger(__name__)

VALID_CATEGORIES = ("work", "life", "education")


def classify(content: str) -> str:
    """
    调用 LLM 判断任务分类

    Args:
        content: 任务内容

    Returns:
        JSON 字符串格式的 LLMResponse
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        response = loop.run_until_complete(chat("classify", content))
    finally:
        loop.close()

    # 验证返回的数据格式
    if response.ok and response.data is not None:
        data = response.data

        # 处理 {"category": "work"} 格式
        if isinstance(data, dict) and "category" in data:
            category = data["category"]
            if category in VALID_CATEGORIES:
                response.data = category
            else:
                response.ok = False
                response.error = "invalid_category"
        # 处理直接返回 "work" 字符串格式
        elif isinstance(data, str):
            if data in VALID_CATEGORIES:
                response.data = data
            else:
                response.ok = False
                response.error = "invalid_category"
        else:
            response.ok = False
            response.error = "invalid_category"

    return response.to_json_string()
