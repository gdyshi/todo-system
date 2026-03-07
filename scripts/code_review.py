#!/usr/bin/env python3
"""
自动 PR 代码审查脚本
使用 Claude API 生成 PR review
"""

import os
import sys
import requests


def get_env_var(name):
    """获取环境变量"""
    value = os.getenv(name)
    if not value:
        print(f"错误: 未找到 {name}", file=sys.stderr)
        sys.exit(1)
    return value


def get_pr_info():
    """获取 PR 信息"""
    token = get_env_var("GITHUB_TOKEN")
    repo = get_env_var("GITHUB_REPOSITORY")
    pr_number = get_env_var("GITHUB_PR_NUMBER")

    # 获取 PR 信息
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_pr_diff():
    """获取 PR 代码差异"""
    token = get_env_var("GITHUB_TOKEN")
    repo = get_env_var("GITHUB_REPOSITORY")
    pr_number = get_env_var("GITHUB_PR_NUMBER")

    # 获取代码差异
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}.files"
    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        },
        timeout=10,
    )
    response.raise_for_status()
    files = response.json()

    # 获取文件内容
    diff_content = []
    for file in files:
        if file.get("patch"):
            diff_content.append(file["patch"])

    return "\n\n".join(diff_content)


def create_review_prompt(diff, pr_info):
    """创建审查提示词"""
    prompt = f"""请审查以下 PR 的代码变更：

## PR 信息
- 标题: {pr_info['title']}
- 作者: {pr_info['user']['login']}
- 分支: {pr_info['head']['ref']} → {pr_info['base']['ref']}

## 代码差异
```diff
{diff[:2000]}
...
```

请提供：
1. 代码质量评估（可读性、可维护性、性能）
2. 潜在问题或改进建议
3. 具体的代码修改建议（如适用）

请以清晰、建设性的语气进行审查。"""
    return prompt


def call_claude_api(prompt):
    """调用 Claude API"""
    api_key = get_env_var("ANTHROPIC_API_KEY")

    # 调用 Claude API
    # 注意：这里使用简单的 requests 调用
    # 实际部署时应该使用官方 SDK

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()

        # 提取 review 内容
        review = result["content"][0]["text"]
        return review

    except Exception as e:
        print(f"调用 Claude API 失败: {e}", file=sys.stderr)
        return None


def post_review_comment(body):
    """发布 PR 评论"""
    token = get_env_var("GITHUB_TOKEN")
    repo = get_env_var("GITHUB_REPOSITORY")
    pr_number = get_env_var("GITHUB_PR_NUMBER")

    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        },
        json={"body": body},
        timeout=10,
    )
    response.raise_for_status()
    return True


def main():
    """主函数"""
    print("开始 PR 代码审查...")

    # 获取 PR 信息
    pr_info = get_pr_info()
    print(f"PR #{pr_info['number']}: {pr_info['title']}")

    # 获取代码差异
    diff = get_pr_diff()
    if not diff:
        print("警告: 未获取到代码差异", file=sys.stderr)
        review = "⚠️ **警告**: 无法获取代码差异，请检查 PR 配置。"
    else:
        print(f"获取到 {len(diff.splitlines())} 行代码差异")

        # 创建审查提示词
        prompt = create_review_prompt(diff, pr_info)

        # 调用 Claude API
        print("正在调用 Claude API 进行代码审查...")
        review = call_claude_api(prompt)

    # 添加页脚
    review_footer = "\n\n---\n\n*🤖 由 [Claude Code](https://claude.com/claude-code) 自动生成*"
    final_review = review + review_footer

    # 发布评论
    print("发布审查评论...")
    if post_review_comment(final_review):
        print("✅ 代码审查完成！")
        return 0
    else:
        print("❌ 发布评论失败", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
