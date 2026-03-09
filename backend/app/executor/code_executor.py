"""代码执行器 - 调用 Claude Code CLI（使用 GLM Coding Lite API）"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional
import subprocess

logger = logging.getLogger(__name__)


class CodeExecutor:
    """
    代码执行器 - 执行层核心

    类似原文中的 Claude Code，这里调用 Claude Code CLI
    Claude Code 使用 GLM Coding Lite 的 API key 进行认证
    """

    def __init__(self, api_key: str, model: str = "glm-4.7"):
        self.api_key = api_key
        self.model = model

    async def execute_code_task(
        self, prompt: str, context: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        执行代码任务

        编排层调用此方法，传入生成的 prompt
        执行层通过 Claude Code CLI 调用 GLM Coding Lite API，返回代码和结果

        Args:
            prompt: 编排层生成的精确 prompt
            context: 额外的上下文信息
            **kwargs: 其他参数（如工作目录、输出格式等）

        Returns:
            {
                "success": bool,
                "code": str,  # 生成的代码
                "explanation": str,  # 代码解释
                "error": str | None  # 错误信息
            }
        """
        try:
            # 构建完整的 prompt
            full_prompt = self._build_prompt(prompt, context)

            logger.info(
                f"调用 Claude Code CLI: model={self.model}, prompt 长度 {len(prompt)} 字符"
            )

            # 设置环境变量（Claude Code 使用 ANTHROPIC_API_KEY）
            env = {
                "ANTHROPIC_API_KEY": self.api_key,
                "PATH": "/home/gdyshi/.nvm/versions/node/v24.14.0/bin:"
                + "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            }

            # 构建 Claude Code CLI 命令
            # --print: 非交互模式，直接返回结果
            # --model: 指定模型
            # --output-format json: 返回 JSON 格式
            # --dangerously-skip-permissions: 跳过权限检查（全权运行）
            cmd = [
                "/home/gdyshi/.nvm/versions/node/v24.14.0/bin/claude",
                "--model",
                self.model,
                "--print",
                "--output-format",
                "json",
                "--dangerously-skip-permissions",
            ]

            # 执行命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, **env},
            )

            # 使用 wait_for 处理超时
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(input=full_prompt.encode()), timeout=60.0
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise

            if process.returncode != 0:
                error_output = stderr.decode().strip()
                logger.error(f"Claude Code CLI 执行失败: {error_output}")
                return {
                    "success": False,
                    "error": f"Claude Code CLI 错误: {error_output}",
                    "code": None,
                    "explanation": None,
                }

            # 解析输出
            output = stdout.decode().strip()
            return self._parse_output(output)

        except asyncio.TimeoutError:
            logger.error("Claude Code CLI 超时")
            return {
                "success": False,
                "error": "执行超时",
                "code": None,
                "explanation": None,
            }
        except Exception as e:
            logger.error(f"执行代码任务失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "code": None,
                "explanation": None,
            }

    def _build_prompt(self, task_prompt: str, context: Optional[str] = None) -> str:
        """构建完整的 prompt"""
        system_instruction = """你是一个专业的代码助手，专注于编写高质量、可维护的 Python 代码。

你的任务：
1. 根据用户的 prompt 生成代码
2. 代码应该清晰、简洁、符合最佳实践
3. 如果需要数据库操作，使用 SQLAlchemy ORM
4. 如果需要 API，使用 FastAPI
5. 返回格式：简洁的代码说明 + 完整的代码块

请直接给出代码和说明，不要有多余的对话。"""

        if context:
            full_prompt = f"{system_instruction}\n\n上下文信息：\n{context}\n\n任务：\n{task_prompt}"
        else:
            full_prompt = f"{system_instruction}\n\n任务：\n{task_prompt}"

        return full_prompt

    def _parse_output(self, output: str) -> Dict[str, Any]:
        """解析 Claude Code CLI 的输出"""
        try:
            # 尝试解析 JSON 格式
            data = json.loads(output)

            # 提取文本内容
            text = data.get("text", output)

            # 尝试提取代码块
            code = self._extract_code_from_text(text)
            explanation = self._extract_explanation_from_text(text)

            return {
                "success": True,
                "code": code,
                "explanation": explanation,
                "raw_output": output,
            }

        except json.JSONDecodeError:
            # 如果不是 JSON，直接解析文本
            code = self._extract_code_from_text(output)
            explanation = self._extract_explanation_from_text(output)

            return {
                "success": True,
                "code": code,
                "explanation": explanation,
                "raw_output": output,
            }
        except Exception as e:
            logger.error(f"解析输出失败: {str(e)}")
            return {
                "success": False,
                "error": f"解析输出失败: {str(e)}",
                "code": None,
                "explanation": None,
                "raw_output": output,
            }

    def _extract_code_from_text(self, text: str) -> Optional[str]:
        """从文本中提取代码块"""
        import re

        # 匹配 ```python ... ``` 代码块
        pattern = r"```python\n(.*?)\n```"
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            return matches[0].strip()

        # 匹配 ``` ... ``` 代码块（没有语言标识）
        pattern = r"```\n(.*?)\n```"
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            return matches[0].strip()

        return None

    def _extract_explanation_from_text(self, text: str) -> Optional[str]:
        """从文本中提取说明"""
        # 去除代码块后，剩余的内容就是说明
        code = self._extract_code_from_text(text)
        if code:
            explanation = text.replace(f"```python\n{code}\n```", "")
            explanation = explanation.replace(f"```\n{code}\n```", "")
            return explanation.strip()
        return text

    async def execute_sql_query(self, query: str, description: str) -> Dict[str, Any]:
        """
        执行 SQL 查询任务

        这是一个专门的代码生成任务，用于生成 SQL 查询

        Args:
            query: 用户要求的查询描述
            description: 详细的查询说明

        Returns:
            {
                "success": bool,
                "sql": str,  # 生成的 SQL 查询
                "explanation": str,
                "error": str | None
            }
        """
        prompt = f"""作为一个数据库专家，生成一个 SQLAlchemy 查询。

任务描述：{description}

要求：
1. 使用 SQLAlchemy ORM 语法（不是原始 SQL）
2. 返回完整的查询代码
3. 添加必要的注释

查询需求：{query}"""

        result = await self.execute_code_task(prompt)

        # 提取 SQL 部分
        if result["success"] and result["code"]:
            result["sql"] = result["code"]
            result["type"] = "sql"
        else:
            result["sql"] = None
            result["type"] = None

        return result

    async def generate_api_endpoint(
        self,
        endpoint_description: str,
        method: str = "GET",
        input_schema: Optional[Dict] = None,
        output_schema: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        生成 API 端点代码

        Args:
            endpoint_description: 端点功能描述
            method: HTTP 方法（GET, POST, PUT, DELETE）
            input_schema: 输入数据的 JSON Schema
            output_schema: 输出数据的 JSON Schema

        Returns:
            {
                "success": bool,
                "code": str,  # FastAPI 路由代码
                "explanation": str,
                "error": str | None
            }
        """
        prompt = f"""作为一个 FastAPI 专家，生成一个 API 端点。

端点功能：{endpoint_description}
HTTP 方法：{method}"""

        if input_schema:
            prompt += f"\n\n输入 Schema（JSON）：\n{json.dumps(input_schema, indent=2)}"

        if output_schema:
            prompt += (
                f"\n\n输出 Schema（JSON）：\n{json.dumps(output_schema, indent=2)}"
            )

        prompt += """

要求：
1. 使用 FastAPI 路由装饰器
2. 添加 Pydantic 模型验证
3. 添加完整的类型注解
4. 返回标准的 JSON 响应格式
5. 添加错误处理
6. 返回完整的路由代码（可以直接复制粘贴到 FastAPI 应用中）"""

        result = await self.execute_code_task(prompt)
        return result

    async def test_connection(self) -> Dict[str, Any]:
        """
        测试与 GLM Coding Lite 的连接

        Returns:
            连接测试结果
        """
        try:
            result = await self.execute_code_task("写一个简单的 Hello World 函数")
            return {
                "success": result["success"],
                "message": "连接成功" if result["success"] else "连接失败",
                "error": result.get("error"),
            }
        except Exception as e:
            return {"success": False, "message": "连接异常", "error": str(e)}
