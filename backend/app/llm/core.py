"""LLM 核心模块 - 与大语言模型交互"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)


class LLMResponse(BaseModel):
    """LLM 响应模型"""

    ok: bool
    data: Any
    error: Optional[str] = None
    model: str
    usage: Dict[str, int]

    def to_json_string(self) -> str:
        """转换为 JSON 字符串"""
        return self.model_dump_json()


async def chat(task_name: str, content: str) -> LLMResponse:
    """
    调用 LLM API

    Args:
        task_name: 任务名称（用于加载对应的 prompt 文件）
        content: 用户输入内容

    Returns:
        LLMResponse 对象
    """
    model_url = settings.model_url
    model_name = settings.model_name
    model_key = settings.model_key

    # 检查配置
    if not model_url or not model_name or not model_key:
        return LLMResponse(
            ok=False,
            data=None,
            error="unavailable",
            model=model_name,
            usage={"input_tokens": 0, "output_tokens": 0},
        )

    # 加载 system prompt
    system_prompt = _load_prompt(task_name)
    if system_prompt is None:
        return LLMResponse(
            ok=False,
            data=None,
            error="unavailable",
            model=model_name,
            usage={"input_tokens": 0, "output_tokens": 0},
        )

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
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": content},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500,
                },
            )

            if response.status_code != 200:
                logger.warning(f"LLM API 返回非 200 状态码: {response.status_code}")
                return LLMResponse(
                    ok=False,
                    data=None,
                    error="api_error",
                    model=model_name,
                    usage={"input_tokens": 0, "output_tokens": 0},
                )

            data = response.json()
            content_str = data["choices"][0]["message"]["content"].strip()

            # 解析 usage
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            # 尝试解析 JSON
            try:
                parsed_data = json.loads(content_str)
                return LLMResponse(
                    ok=True,
                    data=parsed_data,
                    error=None,
                    model=model_name,
                    usage={"input_tokens": input_tokens, "output_tokens": output_tokens},
                )
            except json.JSONDecodeError:
                return LLMResponse(
                    ok=False,
                    data=None,
                    error="parse_error",
                    model=model_name,
                    usage={"input_tokens": input_tokens, "output_tokens": output_tokens},
                )

    except asyncio.TimeoutError:
        logger.warning(f"LLM API 超时")
        return LLMResponse(
            ok=False,
            data=None,
            error="timeout",
            model=model_name,
            usage={"input_tokens": 0, "output_tokens": 0},
        )
    except Exception as e:
        logger.warning(f"LLM API 调用异常: {e}")
        return LLMResponse(
            ok=False,
            data=None,
            error="api_error",
            model=model_name,
            usage={"input_tokens": 0, "output_tokens": 0},
        )


def _load_prompt(task_name: str) -> Optional[str]:
    """
    加载 prompt 模板

    Args:
        task_name: 任务名称（对应 prompts/{task_name}.md 文件）

    Returns:
        prompt 字符串，失败返回 None
    """
    try:
        prompt_path = Path(__file__).parent / "prompts" / f"{task_name}.md"
        with open(prompt_path, encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.error(f"Prompt 文件不存在: {task_name}.md")
        return None
    except Exception as e:
        logger.error(f"加载 prompt 文件失败: {e}")
        return None
