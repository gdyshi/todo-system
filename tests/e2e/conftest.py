"""Playwright 配置和 fixtures"""
import pytest
from playwright.async_api import async_playwright, Page, Browser


@pytest.fixture
async def browser():
    """
    创建浏览器实例
    
    使用 Chromium（更快）
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        yield browser
        await browser.close()


@pytest.fixture
async def page(browser):
    """
    创建新页面
    
    自动导航到前端页面
    """
    async with await browser.new_page() as page:
        await page.goto("file:///home/gdyshi/.openclaw/workspace/todo-system/frontend/index.html")
        yield page


@pytest.fixture
def frontend_url():
    """
    返回前端 URL
    
    用于测试时动态获取 URL
    """
    return "file:///home/gdyshi/.openclaw/workspace/todo-system/frontend/index.html"


@pytest.fixture
def api_base_url():
    """
    返回 API 基础 URL
    
    用于测试时动态获取 URL
    """
    return "http://localhost:8000/api"
