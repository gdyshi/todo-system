import { test, expect } from '@playwright/test';

// 本地测试使用 localhost:8000（前端 + 后端都在本地运行）
// CI 测试通过 FRONTEND_URL 环境变量指定前端 URL
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:8000';

test.describe('E2E Tests - 创建任务', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
  });

  test('成功创建任务', async ({ page }) => {
    await page.fill('#task-title', 'E2E 测试任务');
    await page.selectOption('#task-category', 'work');
    await page.selectOption('#task-priority', '5');
    await page.fill('#task-description', '这是一个 E2E 测试描述');
    await page.click('button[type="submit"]');
    
    try {
      await page.waitForSelector('.toast-success', { timeout: 5000 });
    } catch {
      await page.waitForTimeout(1000);
    }
    
    await expect(page.locator('.task-item').first()).toBeVisible({ timeout: 5000 });
  });

  test('创建任务（空标题）', async ({ page }) => {
    await page.selectOption('#task-category', 'work');
    await page.click('button[type="submit"]');
  });

  test('创建任务（带截止时间）', async ({ page }) => {
    await page.fill('#task-title', '带截止时间的任务');
    await page.selectOption('#task-category', 'work');
    const now = new Date();
    now.setHours(now.getHours() + 1);
    const dueTime = now.toISOString().slice(0, 16);
    await page.fill('#task-due-time', dueTime);
    await page.click('button[type="submit"]');
    await expect(page.locator('.task-item').first()).toBeVisible({ timeout: 5000 });
  });

  test('创建任务（带子任务）', async ({ page }) => {
    await page.fill('#task-title', '父任务');
    await page.selectOption('#task-category', 'work');
    await page.fill('#task-subtasks', '子任务1\n子任务2\n子任务3');
    await page.click('button[type="submit"]');
    await expect(page.locator('.task-item').first()).toBeVisible({ timeout: 5000 });
  });

  test('创建成功后表单清空', async ({ page }) => {
    await page.fill('#task-title', '测试任务');
    await page.fill('#task-description', '测试描述');
    await page.fill('#task-subtasks', '子任务');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);
    await expect(page.locator('#task-title')).toHaveValue('');
  });
});

test.describe('E2E Tests - 任务列表', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
  });

  test('任务列表显示', async ({ page }) => {
    await expect(page.locator('#tasks-container')).toBeVisible();
    await expect(page.locator('h2:has-text("任务列表")')).toBeVisible();
  });

  test('任务列表筛选（分类）', async ({ page }) => {
    await page.waitForSelector('#tasks-container', { timeout: 10000 });
    await page.click('.filter-btn[data-filter="work"]');
    await page.waitForTimeout(500);
  });

  test('任务计数显示', async ({ page }) => {
    await expect(page.locator('#task-count')).toBeVisible();
    const countText = await page.locator('#task-count').textContent();
    expect(countText).toMatch(/\(\d+\)/);
  });
});
