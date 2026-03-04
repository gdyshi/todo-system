"""E2E 测试：创建任务"""
import pytest
from tests.e2e.conftest import frontend_url


@pytest.mark.e2e
async def test_create_task_success(page, api_base_url):
    """测试：成功创建任务"""
    # 导航到页面
    await page.goto(frontend_url)
    
    # 填写表单
    await page.fill('#task-title', 'E2E 测试任务')
    await page.select_option('#task-category', 'work')
    await page.select_option('#task-priority', '5')
    await page.fill('#task-description', '这是一个 E2E 测试描述')
    
    # 提交表单
    await page.click('button[type="submit"]')
    
    # 等待成功提示
    await page.wait_for_selector('.toast-success', timeout=5000)
    
    # 验证成功提示内容
    toast_text = await page.text_content('.toast-success')
    assert '成功' in toast_text
    
    # 验证任务出现在列表中
    await page.wait_for_selector('.task-item:has-text("E2E 测试任务")', timeout=5000)


@pytest.mark.e2e
async def test_create_task_empty_title(page, api_base_url):
    """测试：创建任务（空标题）"""
    await page.goto(frontend_url)
    
    # 不填写标题
    await page.select_option('#task-category', 'work')
    
    # 尝试提交
    await page.click('button[type="submit"]')
    
    # 等待错误提示（或浏览器验证）
    # 注意：如果前端有 HTML5 验证，可能需要禁用验证


@pytest.mark.e2e
async def test_create_task_with_due_time(page, api_base_url):
    """测试：创建任务（带截止时间）"""
    await page.goto(frontend_url)
    
    # 填写表单
    await page.fill('#task-title', '带截止时间的任务')
    await page.select_option('#task-category', 'work')
    
    # 设置截止时间（1小时后）
    import datetime
    due_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')
    await page.fill('#task-due-time', due_time)
    
    # 提交
    await page.click('button[type="submit"]')
    
    # 等待成功提示
    await page.wait_for_selector('.toast-success', timeout=5000)


@pytest.mark.e2e
async def test_create_task_with_subtasks(page, api_base_url):
    """测试：创建任务（带子任务）"""
    await page.goto(frontend_url)
    
    # 填写表单
    await page.fill('#task-title', '父任务')
    await page.select_option('#task-category', 'work')
    await page.fill('#task-subtasks', '子任务1\n子任务2\n子任务3')
    
    # 提交
    await page.click('button[type="submit"]')
    
    # 等待成功提示
    await page.wait_for_selector('.toast-success', timeout=5000)
    
    # 验证子任务出现在列表中
    await page.wait_for_selector('.subtasks .subtask-item:has-text("子任务1")', timeout=5000)


@pytest.mark.e2e
async def test_create_task_clears_form(page, api_base_url):
    """测试：创建成功后表单清空"""
    await page.goto(frontend_url)
    
    # 填写表单
    await page.fill('#task-title', '测试任务')
    await page.fill('#task-description', '测试描述')
    await page.fill('#task-subtasks', '子任务')
    
    # 提交
    await page.click('button[type="submit"]')
    
    # 等待成功提示
    await page.wait_for_selector('.toast-success', timeout=5000)
    
    # 验证表单已清空
    title_value = await page.input_value('#task-title')
    assert title_value == ""
    
    description_value = await page.input_value('#task-description')
    assert description_value == ""


@pytest.mark.e2e
async def test_create_task_with_location_json(page, api_base_url):
    """测试：创建任务（带地点 JSON）"""
    await page.goto(frontend_url)
    
    # 填写表单
    await page.fill('#task-title', '地点测试任务')
    await page.fill('#task-location', '{"lat": 31.2304, "lon": 121.4737, "city": "上海"}')
    
    # 提交
    await page.click('button[type="submit"]')
    
    # 等待成功提示
    await page.wait_for_selector('.toast-success', timeout=5000)
