"""测试双层架构的脚本 - 使用 Claude Code CLI"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.executor.code_executor import CodeExecutor
from app.config import settings


async def test_code_executor():
    """测试执行层 - 调用 Claude Code CLI"""

    print("=" * 60)
    print("测试双层架构 - 执行层")
    print("=" * 60)
    print()

    # 初始化执行器
    executor = CodeExecutor(
        api_key=settings.glm_api_key,
        model=settings.glm_model
    )

    print(f"GLM API Key: {settings.glm_api_key[:20]}...")
    print(f"GLM 模型: {settings.glm_model}")
    print()

    # 测试 1: 通用代码生成
    print("测试 1: 通用代码生成")
    print("-" * 60)

    prompt = """
编写一个 Python 函数，用于计算任务列表的完成率。

输入：任务列表，每个任务有 status 字段（"completed" 或其他）
输出：完成率（百分比）

示例：
```python
tasks = [
    {"status": "completed"},
    {"status": "pending"},
    {"status": "completed"},
]
# 输出: 66.67
```
"""

    result = await executor.execute_code_task(prompt)

    print(f"成功: {result['success']}")
    if result['success']:
        if result['code']:
            print(f"\n生成的代码:\n{result['code']}")
        if result['explanation']:
            print(f"\n解释: {result['explanation']}")
    else:
        print(f"错误: {result['error']}")

    print()

    # 测试 2: SQL 查询生成
    print("测试 2: SQL 查询生成")
    print("-" * 60)

    result = await executor.execute_sql_query(
        query="获取所有未完成的高优先级任务",
        description="使用 Task 模型，高优先级是 priority > 5，未完成是 status != 'completed'"
    )

    print(f"成功: {result['success']}")
    if result['success']:
        if result['sql']:
            print(f"\n生成的 SQL:\n{result['sql']}")
        if result['explanation']:
            print(f"\n解释: {result['explanation']}")
    else:
        print(f"错误: {result['error']}")

    print()

    # 测试 3: 连接测试
    print("测试 3: 连接测试")
    print("-" * 60)

    test_result = await executor.test_connection()

    print(f"成功: {test_result['success']}")
    print(f"消息: {test_result['message']}")
    if test_result.get('error'):
        print(f"错误: {test_result['error']}")

    print()
    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_code_executor())
