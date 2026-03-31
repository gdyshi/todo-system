"""性能基准测试

使用 Playwright 收集 Core Web Vitals 指标

Core Web Vitals:
- LCP (Largest Contentful Paint): 最大内容绘制
- FID (First Input Delay): 首次输入延迟
- CLS (Cumulative Layout Shift): 累积布局偏移
"""
import os
import json
import pytest
from playwright.async_api import Page


class PerformanceMetrics:
    """性能指标收集器"""
    
    def __init__(self, page: Page):
        self.page = page
        self.metrics = {}
    
    async def collect(self) -> dict:
        """收集页面性能指标"""
        # 获取 navigation timing
        navigation_timing = await self.page.evaluate("""
            () => {
                const [navigation] = performance.getEntriesByType('navigation');
                return {
                    // 基础时间指标
                    fetchStart: navigation.fetchStart,
                    domainLookupStart: navigation.domainLookupStart,
                    domainLookupEnd: navigation.domainLookupEnd,
                    connectStart: navigation.connectStart,
                    connectEnd: navigation.connectEnd,
                    requestStart: navigation.requestStart,
                    responseStart: navigation.responseStart,
                    responseEnd: navigation.responseEnd,
                    domInteractive: navigation.domInteractive,
                    domContentLoadedEventEnd: navigation.domContentLoadedEventEnd,
                    domComplete: navigation.domComplete,
                    loadEventEnd: navigation.loadEventEnd,
                    
                    // 计算衍生指标
                    dnsTime: navigation.domainLookupEnd - navigation.domainLookupStart,
                    tcpTime: navigation.connectEnd - navigation.connectStart,
                    ttfb: navigation.responseStart - navigation.requestStart,
                    contentDownload: navigation.responseEnd - navigation.responseStart,
                    domParse: navigation.domInteractive - navigation.responseEnd,
                    domReady: navigation.domContentLoadedEventEnd - navigation.domInteractive,
                    resourceLoad: navigation.loadEventEnd - navigation.domComplete,
                    
                    // 总页面加载时间
                    totalLoadTime: navigation.loadEventEnd - navigation.fetchStart,
                };
            }
        """)
        
        # 获取 Paint timing (LCP, FCP)
        paint_timing = await self.page.evaluate("""
            () => {
                const paintEntries = performance.getEntriesByType('paint');
                const result = {};
                paintEntries.forEach(entry => {
                    result[entry.name] = entry.startTime;
                });
                return result;
            }
        """)
        
        # 获取 LCP 详细信息
        lcp_detail = await self.page.evaluate("""
            () => {
                return new Promise((resolve) => {
                    new PerformanceObserver((entryList) => {
                        const entries = entryList.getEntries();
                        const lastEntry = entries[entries.length - 1];
                        resolve({
                            lcp: lastEntry.startTime,
                            lcpElement: lastEntry.element?.tagName + (lastEntry.element?.id ? '#' + lastEntry.element.id : '') + (lastEntry.element?.className ? '.' + lastEntry.element.className.split(' ').join('.') : ''),
                            lcpSize: lastEntry.size,
                        });
                    }).observe({ type: 'largest-contentful-paint', buffered: true });
                    
                    // 超时处理
                    setTimeout(() => resolve({ lcp: null }), 3000);
                });
            }
        """)
        
        # 获取 CLS
        cls = await self.page.evaluate("""
            () => {
                let clsValue = 0;
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (!entry.hadRecentInput) {
                            clsValue += entry.value;
                        }
                    }
                });
                observer.observe({ type: 'layout-shift', buffered: true });
                
                // 返回当前累积值
                return new Promise((resolve) => {
                    setTimeout(() => {
                        resolve(clsValue);
                        observer.disconnect();
                    }, 1000);
                });
            }
        """)
        
        return {
            **navigation_timing,
            'paint': paint_timing,
            'lcp_detail': lcp_detail,
            'cls': cls,
        }


@pytest.fixture
async def performance_metrics(page):
    """创建性能指标收集器"""
    metrics = PerformanceMetrics(page)
    yield metrics
    # 测试结束后自动收集


@pytest.mark.performance
async def test_page_load_time(performance_metrics, page):
    """测试：页面加载时间 < 3秒"""
    metrics = performance_metrics.metrics
    
    # 触发指标收集
    await page.evaluate("() => {}")  # 确保页面已加载
    await page.wait_for_load_state('networkidle')
    
    # 收集指标
    collected = await performance_metrics.collect()
    
    # 验证加载时间
    total_load_time = collected.get('totalLoadTime', 0)
    assert total_load_time < 3000, f"页面加载时间 {total_load_time}ms 超过 3秒"
    print(f"\n📊 页面加载时间: {total_load_time}ms")


@pytest.mark.performance
async def test_first_contentful_paint(performance_metrics, page):
    """测试：首次内容绘制 (FCP) < 2秒"""
    collected = await performance_metrics.collect()
    
    fcp = collected.get('paint', {}).get('first-contentful-paint', 0)
    assert fcp < 2000, f"FCP {fcp}ms 超过 2秒"
    print(f"\n📊 FCP: {fcp}ms")


@pytest.mark.performance
async def test_largest_contentful_paint(performance_metrics, page):
    """测试：最大内容绘制 (LCP) < 2.5秒"""
    collected = await performance_metrics.collect()
    
    lcp = collected.get('lcp_detail', {}).get('lcp', 0)
    assert lcp < 2500, f"LCP {lcp}ms 超过 2.5秒"
    print(f"\n📊 LCP: {lcp}ms")
    
    # 打印 LCP 元素
    lcp_element = collected.get('lcp_detail', {}).get('lcpElement', 'N/A')
    print(f"📊 最大内容元素: {lcp_element}")


@pytest.mark.performance
async def test_cumulative_layout_shift(performance_metrics, page):
    """测试：累积布局偏移 (CLS) < 0.1"""
    # 先与页面交互，触发可能的布局偏移
    await performance_metrics.page.click('body')
    await performance_metrics.page.wait_for_timeout(500)
    
    collected = await performance_metrics.collect()
    cls = collected.get('cls', 0)
    assert cls < 0.1, f"CLS {cls} 超过 0.1"
    print(f"\n📊 CLS: {cls}")


@pytest.mark.performance
async def test_time_to_first_byte(performance_metrics, page):
    """测试：首字节时间 (TTFB) < 800ms"""
    collected = await performance_metrics.collect()
    
    ttfb = collected.get('ttfb', 0)
    assert ttfb < 800, f"TTFB {ttfb}ms 超过 800ms"
    print(f"\n📊 TTFB: {ttfb}ms")


@pytest.mark.performance
async def test_dom_interactive(performance_metrics, page):
    """测试：DOM 可交互时间 (TTI) < 3.5秒"""
    collected = await performance_metrics.collect()
    
    dom_interactive = collected.get('domInteractive', 0)
    assert dom_interactive < 3500, f"TTI {dom_interactive}ms 超过 3.5秒"
    print(f"\n📊 TTI: {dom_interactive}ms")


@pytest.mark.performance
async def test_network_metrics(performance_metrics, page):
    """测试：网络性能指标"""
    collected = await performance_metrics.collect()
    
    dns_time = collected.get('dnsTime', 0)
    tcp_time = collected.get('tcpTime', 0)
    ttfb = collected.get('ttfb', 0)
    
    print(f"\n📊 网络指标:")
    print(f"   DNS 查询: {dns_time}ms")
    print(f"   TCP 连接: {tcp_time}ms")
    print(f"   TTFB: {ttfb}ms")
    
    # DNS 应该很快
    assert dns_time < 500, f"DNS 查询时间 {dns_time}ms 过长"
    
    # TCP 连接应该很快
    assert tcp_time < 500, f"TCP 连接时间 {tcp_time}ms 过长"


@pytest.mark.performance
async def test_api_response_time(performance_metrics, page):
    """测试：API 响应时间 < 500ms"""
    import time
    
    api_base_url = os.environ.get('API_BASE_URL', 'https://todo-system-msvx.onrender.com/api')
    
    # 测试获取任务列表 API
    start_time = time.time()
    response = await performance_metrics.page.evaluate(f"""
        async () => {{
            const res = await fetch('{api_base_url}/tasks');
            return await res.json();
        }}
    """)
    end_time = time.time()
    
    api_time = (end_time - start_time) * 1000
    print(f"\n📊 API 响应时间: {api_time:.2f}ms")
    
    assert api_time < 500, f"API 响应时间 {api_time:.2f}ms 超过 500ms"
