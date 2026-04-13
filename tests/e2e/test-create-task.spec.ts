import { test, expect } from '@playwright/test';

// E2E tests use environment variables, defaulting to local development server
// WARNING: Never run E2E tests against production unless you have a dedicated test database!
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:5173';
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api';

test.describe('E2E Tests - 创建任务', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
    // 等待页面基本加载
    await page.waitForSelector('#task-title', { timeout: 15000 });
  });

  test('成功创建任务', async ({ page }) => {
    await page.fill('#task-title', 'E2E 测试任务');
    await page.selectOption('#task-category', 'work');
    await page.selectOption('#task-priority', '5');
    await page.fill('#task-description', '这是一个 E2E 测试描述');
    await page.click('button[type="submit"]');
    
    // 等待任务出现在列表中
    await expect(page.locator('.task-item').first()).toBeVisible({ timeout: 10000 });
  });

  test('创建任务（空标题）', async ({ page }) => {
    await page.selectOption('#task-category', 'work');
    await page.click('button[type="submit"]');
    // 空标题时表单不应提交，页面不应有变化
  });

  test('创建任务（带截止时间）', async ({ page }) => {
    await page.fill('#task-title', '带截止时间的任务');
    await page.selectOption('#task-category', 'work');
    const now = new Date();
    now.setHours(now.getHours() + 1);
    const dueTime = now.toISOString().slice(0, 16);
    await page.fill('#task-due-time', dueTime);
    await page.click('button[type="submit"]');
    await expect(page.locator('.task-item').first()).toBeVisible({ timeout: 10000 });
  });

  test('创建任务（带子任务）', async ({ page }) => {
    await page.fill('#task-title', '父任务');
    await page.selectOption('#task-category', 'work');
    await page.fill('#task-subtasks', '子任务1\n子任务2\n子任务3');
    await page.click('button[type="submit"]');
    await expect(page.locator('.task-item').first()).toBeVisible({ timeout: 10000 });
  });

  test('创建成功后表单清空', async ({ page }) => {
    await page.fill('#task-title', '测试任务');
    await page.fill('#task-description', '测试描述');
    await page.fill('#task-subtasks', '子任务');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
    await expect(page.locator('#task-title')).toHaveValue('');
  });
});

test.describe('E2E Tests - 任务列表', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForSelector('#tasks-container', { timeout: 15000 });
  });

  test('任务列表显示', async ({ page }) => {
    await expect(page.locator('#tasks-container')).toBeVisible();
  });

  test('任务计数显示', async ({ page }) => {
    await expect(page.locator('#task-count')).toBeVisible();
  });
});
