"""Playwright 配置和 fixtures"""
import os
import pytest
import httpx
from playwright.async_api import async_playwright, Page


def get_frontend_url():
    """获取前端 URL，支持环境变量配置"""
    return os.environ.get('FRONTEND_URL', 'https://todo-system-psi.vercel.app')


def get_api_base_url():
    """获取 API 基础 URL，支持环境变量配置"""
    return os.environ.get('API_BASE_URL', 'https://todo-system-msvx.onrender.com/api')


@pytest.fixture(scope="session")
async def browser():
    """
    创建浏览器实例
    
    使用 Chromium（更快）
    headless 模式在 CI 中自动启用
    """
    async with async_playwright() as p:
        is_ci = os.environ.get('CI', 'false').lower() == 'true'
        browser = await p.chromium.launch(
            headless=True,  # CI 中使用 headless
            args=['--no-sandbox']  # Docker/CI 环境优化
        )
        yield browser
        await browser.close()


@pytest.fixture
async def page(browser):
    """
    创建新页面
    
    自动导航到前端页面（从环境变量或默认 URL）
    """
    frontend = get_frontend_url()
    async with await browser.new_page() as page:
        # 等待网络空闲后再继续
        await page.goto(frontend, wait_until='networkidle')
        yield page


@pytest.fixture
def frontend_url():
    """
    返回前端 URL
    
    用于测试时动态获取 URL
    """
    return get_frontend_url()


@pytest.fixture
def api_base_url():
    """
    返回 API 基础 URL
    
    用于测试时动态获取 URL
    """
    return get_api_base_url()


@pytest.fixture
async def api_client(api_base_url):
    """
    返回异步 HTTP 客户端
    
    用于 E2E 测试中直接调用 API
    """
    async with httpx.AsyncClient(base_url=api_base_url) as client:
        yield client


@pytest.fixture
async def cleanup_tasks(api_client):
    """
    测试后清理：删除所有测试创建的任务
    
    使用方式：
    async def test_something(cleanup_tasks):
        # 创建任务
        await cleanup_tasks.add_task(task_id)
        # 测试...
    """
    created_task_ids = []
    
    class Cleanup:
        def add_task(self, task_id):
            created_task_ids.append(task_id)
        
        async def cleanup(self):
            for task_id in created_task_ids:
                try:
                    await api_client.delete(f"/tasks/{task_id}")
                except Exception:
                    pass
    
    cleanup = Cleanup()
    yield cleanup
    await cleanup.cleanup()
