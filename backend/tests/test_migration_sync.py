"""
测试 alembic 迁移文件与模型的同步性。

验证思路：
1. 解析模型定义，获取所有表名和列名
2. 解析 alembic 迁移文件的 DDL 操作，获取所有表名和列名
3. 对比两者是否一致

这样不依赖数据库，避免 SQLite/PostgreSQL 兼容性问题。
"""

import pytest
import re
from app.models import Base, Task, IPMapping, TaskLocation


def _get_model_tables_and_columns():
    """从 SQLAlchemy 模型提取表名和列名"""
    result = {}
    for table_name, table in Base.metadata.tables.items():
        result[table_name] = sorted([col.name for col in table.columns])
    return result


def _get_migration_tables_and_columns():
    """从 alembic 迁移文件提取操作过的表名和列名"""
    migrations_dir = "migrations/versions"
    import os

    tables = {}
    for fname in sorted(os.listdir(migrations_dir)):
        if not fname.endswith(".py"):
            continue
        fpath = os.path.join(migrations_dir, fname)
        with open(fpath) as f:
            content = f.read()

        # 提取 create_table 操作
        # 匹配 op.create_table("table_name", ...)
        create_pattern = r'op\.create_table\(\s*["\'](\w+)["\']'
        for match in re.finditer(create_pattern, content):
            table_name = match.group(1)
            # 提取该 create_table 块内的所有列
            # 找到这个匹配后的整个函数调用内容
            start = match.end()
            # 简单方式：提取到下一个 op. 或函数结束
            block = content[start : start + 2000]
            col_pattern = r'sa\.Column\(\s*["\'](\w+)["\']'
            cols = set(re.findall(col_pattern, block))
            if table_name not in tables:
                tables[table_name] = set()
            tables[table_name].update(cols)

        # 提取 add_column 操作
        add_pattern = (
            r'op\.add_column\(\s*["\'](\w+)["\']\s*,\s*sa\.Column\(\s*["\'](\w+)["\']'
        )
        for match in re.finditer(add_pattern, content):
            table_name = match.group(1)
            col_name = match.group(2)
            if table_name not in tables:
                tables[table_name] = set()
            tables[table_name].add(col_name)

    return {k: sorted(v) for k, v in tables.items()}


def test_migration_covers_all_model_tables():
    """验证迁移文件覆盖了模型定义的所有表"""
    model_tables = set(_get_model_tables_and_columns().keys())
    migration_tables = set(_get_migration_tables_and_columns().keys())

    missing_tables = model_tables - migration_tables
    assert not missing_tables, (
        f"迁移文件缺少以下表: {missing_tables}。"
        f"模型定义了 {sorted(model_tables)}，迁移只覆盖了 {sorted(migration_tables)}"
    )


def test_migration_covers_all_model_columns():
    """验证迁移文件覆盖了模型定义的所有列"""
    model_schema = _get_model_tables_and_columns()
    migration_schema = _get_migration_tables_and_columns()

    errors = []
    for table_name, model_cols in model_schema.items():
        if table_name not in migration_schema:
            errors.append(f"表 '{table_name}' 在迁移文件中不存在")
            continue
        missing_cols = set(model_cols) - set(migration_schema.get(table_name, []))
        if missing_cols:
            errors.append(
                f"表 '{table_name}' 缺少列: {sorted(missing_cols)}。"
                f"模型定义: {model_cols}，迁移定义: {migration_schema[table_name]}"
            )

    assert not errors, "迁移文件与模型不同步:\n" + "\n".join(errors)
