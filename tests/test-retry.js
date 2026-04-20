// 测试 fetchWithRetry 函数
// 这个测试模拟了不同的场景：正常返回、失败后重试成功、全部失败

// 模拟 fetch 函数
let fetchCallCount = 0;
let fetchBehavior = 'success'; // 'success', 'retry-then-success', 'always-fail'

function mockFetch(url, options) {
    fetchCallCount++;
    console.log(`[fetch] 调用 #${fetchCallCount}: ${url}`);

    switch (fetchBehavior) {
        case 'success':
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ message: 'success' })
            });

        case 'retry-then-success':
            if (fetchCallCount < 2) {
                // 第一次失败
                return Promise.reject(new Error('Network error'));
            }
            // 第二次成功
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ message: 'success after retry' })
            });

        case 'always-fail':
            return Promise.reject(new Error('Network error'));

        case 'http-error':
            return Promise.resolve({
                ok: false,
                status: 500
            });

        default:
            return Promise.reject(new Error('Unknown behavior'));
    }
}

// 将 fetchWithRetry 的核心逻辑提取出来以便测试
async function fetchWithRetry(url, options = {}, retries = 2, delay = 3000) {
    for (let attempt = 0; attempt <= retries; attempt++) {
        try {
            const response = await mockFetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response;
        } catch (error) {
            if (attempt === retries) {
                throw error;
            }
            console.warn(`请求失败，${delay / 1000}秒后重试 (${attempt + 1}/${retries})...`, url);
            // 为了测试，使用更短的延迟
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }
}

// 测试用例
async function runTests() {
    let passed = 0;
    let failed = 0;

    console.log('\n=== 开始测试 fetchWithRetry ===\n');

    // 测试 1: 正常返回
    console.log('测试 1: 正常返回');
    fetchCallCount = 0;
    fetchBehavior = 'success';
    try {
        const result = await fetchWithRetry('http://test.com/api');
        if (fetchCallCount === 1 && result.ok) {
            console.log('✓ 通过 - 首次调用成功\n');
            passed++;
        } else {
            console.log('✗ 失败 - 首次调用应该成功\n');
            failed++;
        }
    } catch (e) {
        console.log('✗ 失败 - 不应该抛出错误:', e.message, '\n');
        failed++;
    }

    // 测试 2: 失败后重试成功
    console.log('测试 2: 失败后重试成功');
    fetchCallCount = 0;
    fetchBehavior = 'retry-then-success';
    try {
        const result = await fetchWithRetry('http://test.com/api', {}, 2, 100);
        if (fetchCallCount === 2 && result.ok) {
            console.log('✓ 通过 - 重试后成功\n');
            passed++;
        } else {
            console.log(`✗ 失败 - 调用次数: ${fetchCallCount}, ok: ${result.ok}\n`);
            failed++;
        }
    } catch (e) {
        console.log('✗ 失败 - 不应该抛出错误:', e.message, '\n');
        failed++;
    }

    // 测试 3: 全部失败
    console.log('测试 3: 全部失败 (3次尝试)');
    fetchCallCount = 0;
    fetchBehavior = 'always-fail';
    try {
        await fetchWithRetry('http://test.com/api', {}, 2, 100);
        console.log('✗ 失败 - 应该抛出错误\n');
        failed++;
    } catch (e) {
        if (fetchCallCount === 3) {
            console.log('✓ 通过 - 重试3次后抛出错误\n');
            passed++;
        } else {
            console.log(`✗ 失败 - 调用次数应该是3，实际: ${fetchCallCount}\n`);
            failed++;
        }
    }

    // 测试 4: HTTP 错误 (非 ok 响应)
    console.log('测试 4: HTTP 错误 (500) 应该重试');
    fetchCallCount = 0;
    fetchBehavior = 'http-error';
    try {
        await fetchWithRetry('http://test.com/api', {}, 1, 100);
        console.log('✗ 失败 - 应该抛出错误\n');
        failed++;
    } catch (e) {
        if (fetchCallCount === 2) {
            console.log('✓ 通过 - HTTP错误导致重试\n');
            passed++;
        } else {
            console.log(`✗ 失败 - 调用次数应该是2，实际: ${fetchCallCount}\n`);
            failed++;
        }
    }

    // 测试 5: 自定义重试次数
    console.log('测试 5: 自定义重试次数为1');
    fetchCallCount = 0;
    fetchBehavior = 'always-fail';
    try {
        await fetchWithRetry('http://test.com/api', {}, 1, 100);
        console.log('✗ 失败 - 应该抛出错误\n');
        failed++;
    } catch (e) {
        if (fetchCallCount === 2) {
            console.log('✓ 通过 - 重试1次(总共2次调用)后抛出错误\n');
            passed++;
        } else {
            console.log(`✗ 失败 - 调用次数应该是2，实际: ${fetchCallCount}\n`);
            failed++;
        }
    }

    // 总结
    console.log('=== 测试完成 ===');
    console.log(`通过: ${passed}/${passed + failed}`);
    console.log(`失败: ${failed}/${passed + failed}`);

    if (failed === 0) {
        console.log('\n✓ 所有测试通过！');
        process.exit(0);
    } else {
        console.log('\n✗ 部分测试失败');
        process.exit(1);
    }
}

// 运行测试
runTests().catch(err => {
    console.error('测试运行出错:', err);
    process.exit(1);
});
