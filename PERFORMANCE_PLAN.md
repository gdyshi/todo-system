# 性能测试升级计划 - 方案 B

> 本文档记录性能测试的升级路径，从方案 A（当前实现）到方案 B（进阶追踪）

## 📊 方案 A vs 方案 B

| 特性 | 方案 A | 方案 B |
|------|--------|--------|
| E2E 测试 | ✅ Playwright | ✅ Playwright |
| 性能基准 | ✅ Playwright 内置指标 | ✅ Lighthouse CI |
| 性能趋势追踪 | ❌ 无 | ✅ 有 |
| 性能回归告警 | ❌ 无 | ✅ 有 |
| Dashboard | ❌ 无 | ✅ Lighthouse CI Dashboard |
| 配置复杂度 | 低 | 中 |
| 额外依赖 | 无 | Lighthouse CI Server |

---

## 🎯 方案 B 核心组件

### 1. Lighthouse CI
- **作用**：持续追踪性能趋势，自动检测性能回归
- **官网**：https://github.com/GoogleChrome/lighthouse-ci
- **特点**：
  - 与 GitHub Actions 无缝集成
  - 自动在 PR 评论中发布性能报告
  - 性能下降自动告警

### 2. 性能指标目标

根据 Core Web Vitals 标准：

| 指标 | 名称 | 目标值 | 优秀值 |
|------|------|--------|--------|
| LCP | Largest Contentful Paint | < 2.5s | < 1.5s |
| FID | First Input Delay | < 100ms | < 50ms |
| CLS | Cumulative Layout Shift | < 0.1 | < 0.05 |
| FCP | First Contentful Paint | < 1.8s | < 1.0s |
| TTFB | Time to First Byte | < 800ms | < 400ms |

### 3. 实现架构

```
GitHub Actions
├── e2e-test.yml           # Playwright E2E 测试
├── performance-test.yml     # 性能基准测试（方案 A）
└── lighthouse-ci.yml       # Lighthouse CI 配置（方案 B）

├── lighthouserc.json       # Lighthouse CI 配置
└── tests/
    ├── e2e/
    │   └── todo.spec.ts
    └── performance/
        └── lighthouse.spec.ts
```

---

## 📋 升级步骤

### 升级到方案 B 需要做的事：

1. **安装 Lighthouse CI**
   ```bash
   npm install -g @lhci/cli
   ```

2. **配置 lighthouserc.json**
   ```json
   {
     "ci": {
       "collect": {
         "url": ["https://staging.example.com"],
         "numberOfRuns": 3
       },
       "assert": {
         "assertions": {
           "categories:performance": ["error", {"minScore": 0.8}],
           "categories:accessibility": ["error", {"minScore": 0.9}]
         }
       },
       "upload": {
         "target": "lhci"
       }
     }
   }
   ```

3. **创建 lighthouse-ci.yml workflow**

4. **（可选）部署 Lighthouse CI Server**
   - 用于存储历史数据
   - 提供可视化 Dashboard
   - 官网提供免费云端存储（limited）

---

## ❓ 待确认事项

- [ ] 是否需要部署 Lighthouse CI Server？
- [ ] 性能基准分数目标设定（默认 0.8）
- [ ] 性能回归告警通知方式（PR 评论 / Email / Slack）

---

## 📅 创建时间
2026-03-31

## 📝 备注
- 方案 A 是当前实现，已足够满足基础需求
- 方案 B 适合需要持续追踪性能趋势的团队
- 可以随时从方案 A 升级到方案 B
