#!/usr/bin/env python3
"""
Secret Detection Script for CI/CD
Scans source code for hardcoded API keys, tokens, passwords, and other secrets.
Exit code 1 if any potential secrets are found.

Usage: python secret-scan.py [directory]
"""

import os
import re
import subprocess
import sys

# Patterns that indicate hardcoded secrets
SECRET_PATTERNS = [
    (re.compile(r'(?:api[_-]?key|apikey)\s*[=:]\s*["\'][a-zA-Z0-9_\-]{20,}["\']', re.IGNORECASE),
     "Hardcoded API Key"),

    (re.compile(r'(?:secret[_-]?key|secret)\s*[=:]\s*["\'][a-zA-Z0-9_\-]{20,}["\']', re.IGNORECASE),
     "Hardcoded Secret Key"),

    (re.compile(r'(?:password|passwd|pwd)\s*[=:]\s*["\'][^\s"\'\$]{8,}["\']', re.IGNORECASE),
     "Hardcoded Password"),

    (re.compile(r'Bearer\s+[A-Za-z0-9_\-\.]{20,}', re.IGNORECASE),
     "Hardcoded Bearer Token"),

    (re.compile(r'sk-[a-zA-Z0-9]{20,}', re.IGNORECASE),
     "Potential OpenAI/Stripe API Key"),

    (re.compile(r'pk-[a-zA-Z0-9]{20,}', re.IGNORECASE),
     "Potential Public API Key"),

    (re.compile(r'rk-[a-zA-Z0-9]{20,}', re.IGNORECASE),
     "Potential API Key (rk- prefix)"),

    (re.compile(r'AKIA[0-9A-Z]{16}', re.IGNORECASE),
     "Potential AWS Access Key"),

    (re.compile(r'(?:token|auth|access[_-]?key)\s*[=:]\s*["\'][a-zA-Z0-9_\-\.]{30,}["\']', re.IGNORECASE),
     "Hardcoded Token/Auth Key"),

    (re.compile(r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----', re.IGNORECASE),
     "Private Key File"),

    (re.compile(r'(?:webhook_url|slack_webhook|discord_webhook)\s*[=:]\s*["\']https?://[^\s"\']+[^\s"\']', re.IGNORECASE),
     "Hardcoded Webhook URL"),
]

# Directories to skip
SKIP_DIRS = {
    'node_modules', '.git', '__pycache__', 'build', 'dist',
    '.venv', 'venv', '.tox', '.mypy_cache', '.pytest_cache',
    'coverage', 'htmlcov', '.nyc_output',
}

# Extensions to scan
SCAN_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte',
    '.yml', '.yaml', '.json', '.toml', '.ini', '.cfg',
    '.sh', '.bash', '.zsh', '.fish', '.bat', '.cmd', '.ps1',
    '.go', '.rs', '.java', '.kt', '.rb', '.php',
    '.c', '.cpp', '.h', '.hpp', '.cs', '.tf', '.hcl',
    '.md', '.txt', '.rst',
}

# Environment files (only scan if git-tracked)
ENV_FILENAMES = {'.env', '.env.local', '.env.production', '.env.development',
                 '.env.staging', '.env.test', '.env.backup'}

# False positive patterns
FALSE_POSITIVE_PATTERNS = [
    re.compile(r'#[^"\']*(?:example|test|placeholder|fake|dummy|sample|todo|xxx|replace|your[_-]?\w+[_-]?(?:here|key|token))', re.IGNORECASE),
    re.compile(r'\$\{[A-Z_]+\}'),
    re.compile(r'\{\{[A-Z_]+\}\}'),
    re.compile(r'os\.environ'),
    re.compile(r'os\.getenv'),
    re.compile(r'process\.env'),
    re.compile(r'getenv'),
]


def is_false_positive(line):
    for pattern in FALSE_POSITIVE_PATTERNS:
        if pattern.search(line):
            return True
    return False


def get_git_tracked_files(repo_root):
    """Get list of git-tracked files."""
    try:
        result = subprocess.run(
            ['git', 'ls-files'],
            capture_output=True, text=True,
            cwd=repo_root, timeout=30
        )
        return set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
    except Exception:
        return None  # If git is not available, scan everything


def should_scan_file(filepath, git_tracked):
    """Determine if a file should be scanned."""
    basename = os.path.basename(filepath)
    # Env files: only scan if git-tracked
    if basename in ENV_FILENAMES or basename.startswith('.env'):
        if git_tracked is not None:
            rel = os.path.relpath(filepath)
            # Normalize path separators for comparison
            rel_normalized = rel.replace('\\', '/')
            return rel_normalized in git_tracked
        return False  # Default: skip env files if git info unavailable
    _, ext = os.path.splitext(filepath)
    return ext.lower() in SCAN_EXTENSIONS


def scan_directory(directory):
    findings = []
    git_tracked = get_git_tracked_files(directory)

    if git_tracked is not None:
        print(f"Found {len(git_tracked)} git-tracked files")
    else:
        print("Git not available - scanning all non-env files")

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            filepath = os.path.join(root, filename)
            if not should_scan_file(filepath, git_tracked):
                continue
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern, description in SECRET_PATTERNS:
                            if pattern.search(line) and not is_false_positive(line):
                                findings.append({
                                    'file': filepath,
                                    'line': line_num,
                                    'description': description,
                                    'content': line.strip()[:150],
                                })
            except (OSError, PermissionError):
                pass

    return findings


def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    print("=" * 60)
    print("SECRET DETECTION SCAN")
    print("=" * 60)
    print(f"Scanning: {target_dir}")
    print()

    findings = scan_directory(target_dir)

    if findings:
        print(f"CRITICAL: Found {len(findings)} potential secret(s)!")
        print("API keys/secrets MUST NOT be hardcoded in source code!")
        print()
        for f in findings:
            rel_path = os.path.relpath(f['file'], target_dir)
            print(f"  [CRITICAL] {rel_path}:{f['line']}")
            print(f"    Type: {f['description']}")
            print(f"    Content: {f['content']}")
            print()
        print("=" * 60)
        print("ACTION REQUIRED:")
        print("  1. Remove hardcoded secrets from source code")
        print("  2. Use environment variables or secret management")
        print("  3. Rotate any exposed credentials")
        print("  4. Use git-filter-repo to clean git history")
        print("=" * 60)
        sys.exit(1)
    else:
        print("PASS: No hardcoded secrets detected.")
        sys.exit(0)


if __name__ == '__main__':
    main()
