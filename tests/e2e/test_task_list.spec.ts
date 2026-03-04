"""E2E 测试：任务列表"""
import pytest
from tests.e2e.conftest import frontend_url


@pytest.mark.e2e
async def test_task_list_displays(page, api_base_url):
    """测试：任务列表显示"""
    await page.goto(frontend_url)
    
    # 等待任务列表加载
    await page.wait_for_selector('#tasks-container', timeout=5000)
    
    # 验证标题
    title_text = await page.text_content('h2:has-text("任务列表")')
    assert '任务列表' in title_text


@pytest.mark.e2e
async def test_task_list_filter_category(page, api_base_url):
    """测试：任务列表筛选（分类）"""
    # 先创建不同分类的任务（通过 API）
    import httpx
    async with httpx.AsyncClient() as client:
        await client.post(f"{api_base_url}/tasks", json={"title": "工作任务", "category": "work"})
        await client.post(f"{api_base_url}/tasks", json={"title": "生活任务", "category": "life"})
    
    await page.goto(frontend_url)
    await page.wait_for_selector('.task-item', timeout=5000)
    
    # 点击工作分类按钮
    await page.click('.filter-btn[data-filter="work"]')
    
    # 等待筛选更新
    await page.wait_for_timeout(500)
    
    # 验证只显示工作任务
    task_items = await page.query_selector_all('.task-item')
    
    # 获取所有任务的标题
    for item in task_items:
        title = await item.text_content('.task-title')
        if '工作任务' in title:
            assert True
        else:
            # 非工作任务不应该显示
            assert False, f"不应该显示任务: {title}"


@pytest.mark.e2e
async def test_task_list_filter_status(page, api_base_url):
    """测试：任务列表筛选（状态）"""
    await page.goto(frontend_url)
    await page.wait_for_selector('.task-item', timeout=5000)
    
    # 取消"待处理"状态
    pending_checkbox = page.locator('.status-filter[value="pending"]')
    if await pending_checkbox.is_checked():
        await pending_checkbox.uncheck()
    
    # 等待列表更新
    await page.wait_for_timeout(500)
    
    # 验证不显示待处理任务
    task_items = await page.query_selector_all('.task-item')
    for item in task_items:
        # 验证状态徽章
        status_badge = await item.query_selector('.task-badge.pending')
        if status_badge:
            assert False, "不应该显示待处理状态的任务"


@pytest.mark.e2e
async def test_task_count_updates(page, api_base_url):
    """测试：任务计数更新"""
    await page.goto(frontend_url)
    await page.wait_for_selector('#task-count', timeout=5000)
    
    # 获取初始计数
    initial_count = await page.text_content('#task-count')
    
    # 创建一个新任务（通过 API）
    import httpx
    async with httpx.AsyncClient() as client:
        await client.post(f"{api_base_url}/tasks", json={"title": "新任务", "category": "work"})
    
    # 刷新页面
    await page.reload()
    await page.wait_for_timeout(1000)
    
    # 验证计数增加
    new_count = await page.text_content('#task-count')
    assert new_count != initial_count


@pytest.mark.e2e
async def test_task_list_empty_state(page, api_base_url):
    """测试：任务列表空状态"""
    # 清空所有任务（通过 API）
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{api_base_url}/tasks")
        tasks = response.json()
        for task in tasks:
            await client.delete(f"{api_base_url}/tasks/{task['id']}")
    
    await page.goto(frontend_url)
    
    # 等待列表加载
    await page.wait_for_selector('#tasks-container', timeout=5000)
    
    # 验证显示"暂无任务"
    container_text = await page.text_content('#tasks-container')
    assert '暂无任务' in container_text


@pytest.mark.e2e
async def test_task_list_sorting(page, api_base_url):
    """测试：任务列表排序"""
    # 先创建不同优先级的任务
    import httpx
    async with httpx.AsyncClient() as client:
        await client.post(f"{api_base_url}/tasks", json={"title": "低优先级", "priority": 0})
        await client.post(f"{api_base_url}/tasks", json={"title": "高优先级", "priority": 9})
    
    await page.goto(frontend_url)
    await page.wait_for_selector('.task-item', timeout=5000)
    
    # 验证高优先级任务排在前面
    task_items = await page.query_selector_all('.task-item')
    if len(task_items) >= 2:
        first_task_title = await task_items[0].text_content('.task-title')
        last_task_title = await task_items[-1].text_content('.task-title')
        
        # 高优先级应该在前面
        assert '高优先级' in first_task_title or first_task_title in last_task_title
