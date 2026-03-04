"""
Pytest 配置和全局 fixtures

测试数据库：database/test_todo.db（独立于生产数据库）
"""
import pytest
import asyncio
import os
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base
from unittest.mock import AsyncMock


# 数据库路径配置
PROD_DB_PATH = "database/todo.db"
TEST_DB_PATH = "database/test_todo.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环（用于异步测试）"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """
    创建测试数据库引擎

    会话级别 fixture：所有测试共享同一个数据库
    测试结束后自动清理
    """
    # 确保测试数据库路径不同
    assert PROD_DB_PATH != TEST_DB_PATH, "测试数据库和生产数据库不能相同！"

    # 删除旧的测试数据库
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    # 创建测试数据库引擎
    engine = create_engine(f"sqlite:///{TEST_DB_PATH}", echo=False)

    # 创建所有表
    Base.metadata.create_all(engine)

    yield engine

    # 清理：删除测试数据库
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture
async def test_db(test_engine) -> AsyncGenerator[Session, None]:
    """
    创建测试数据库会话

    每个测试一个会话
    测试后自动回滚
    """
    TestingSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)
    async with TestingSessionLocal()() as session:
        yield session
        # 回滚事务
        await session.rollback()


@pytest.fixture
def mock_api_key():
    """
    Mock GLM API Key

    用于单元测试，不调用真实 API
    """
    return "test_glm_api_key_12345"


@pytest.fixture
def mock_claude_response():
    """
    Mock Claude Code CLI 的响应

    用于单元测试
    """
    return {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "result": "```python\ndef test():\n    return 'Hello'\n```",
        "stop_reason": None,
        "total_cost_usd": 0.01
    }


@pytest.fixture
def mock_claude_response_json():
    """
    Mock Claude Code CLI 的 JSON 响应
    """
    return {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "result": {
            "type": "result",
            "text": "生成的代码"
        }
    }
