#!/usr/bin/env python3
"""数据库初始化脚本"""

import sys
import os

# 添加app目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.models import init_db

    init_db()
    print("✅ 数据库初始化成功！")
    print("📁 数据库文件位置: database/todo.db")
except ImportError as e:
    print(f"❌ 依赖未安装: {e}")
    print("请先运行: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ 初始化失败: {e}")
    sys.exit(1)
