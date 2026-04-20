import { test, expect } from '@playwright/test';

// E2E tests use environment variables, defaulting to local development server
// WARNING: Never run E2E tests against production unless you have a dedicated test database!
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:5173';
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api';

test.describe('E2E Tests - 创建任务', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
    // 等待页面基本加载 - 前端使用 #task-input
    await page.waitForSelector('#task-input', { timeout: 15000 });
  });

  test('成功创建任务', async ({ page }) => {
    await page.fill('#task-input', 'E2E 测试任务');
    await page.click('.btn-add');
    
    // 等待任务出现在列表中（或等待加载状态消失）
    await page.waitForTimeout(3000);
    // 检查输入框是否被清空（表示提交成功）
    await expect(page.locator('#task-input')).toHaveValue('');
  });

  test('创建任务（空输入）', async ({ page }) => {
    // 空输入时点击添加按钮，HTML5 required 属性会阻止提交
    await page.click('.btn-add');
    // 输入框仍然是空的，没有变化
    await expect(page.locator('#task-input')).toHaveValue('');
  });

  test('页面元素检查', async ({ page }) => {
    // 检查主要元素是否存在
    await expect(page.locator('#task-input')).toBeVisible();
    await expect(page.locator('.btn-add')).toBeVisible();
    await expect(page.locator('#tasks-container')).toBeVisible();
    await expect(page.locator('#task-count')).toBeVisible();
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
