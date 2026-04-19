"""AI 子任务生成器 - 调用外部 AI API 自动生成子任务"""

import json
import logging
from typing import List, Optional
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


async def generate_subtasks(title: str, description: Optional[str] = None) -> List[str]:
    """
    调用 AI API 根据任务标题和描述生成子任务列表

    Args:
        title: 任务标题
        description: 任务描述（可选）

    Returns:
        子任务标题列表，失败时返回空列表
    """
    model_url = settings.model_url
    model_name = settings.model_name
    model_key = settings.model_key

    if not model_url or not model_name or not model_key:
        logger.info("AI 子任务生成未配置（MODEL_URL/MODEL_NAME/MODEL_KEY），跳过自动生成")
        return []

    prompt = _build_prompt(title, description)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                model_url,
                headers={
                    "Authorization": f"Bearer {model_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model_name,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "你是一个任务管理助手。用户会给你一个任务描述，"
                                "你需要将这个任务拆解为 2-5 个具体可执行的子任务。"
                                "只返回 JSON 数组格式，不要其他内容。"
                                "示例：[\"子任务1\", \"子任务2\", \"子任务3\"]"
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500,
                },
            )

            if response.status_code != 200:
                logger.warning(f"AI API 返回非 200 状态码: {response.status_code}")
                return []

            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()

            # 解析 JSON 数组
            subtasks = _parse_subtasks(content)
            logger.info(f"AI 生成子任务成功: {len(subtasks)} 个 - {title}")
            return subtasks

    except Exception as e:
        logger.warning(f"AI 子任务生成失败（不影响主任务创建）: {e}")
        return []


def _build_prompt(title: str, description: Optional[str] = None) -> str:
    """构建生成子任务的 prompt"""
    prompt = f"任务：{title}"
    if description:
        prompt += f"\n描述：{description}"
    prompt += "\n\n请将上述任务拆解为 2-5 个具体可执行的子任务，返回 JSON 数组。"
    return prompt


def _parse_subtasks(content: str) -> List[str]:
    """从 AI 返回内容中解析子任务列表"""
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
    lines = [line.strip().lstrip("0123456789.-) ") for line in content.split("\n") if line.strip()]
    return lines if lines else []
