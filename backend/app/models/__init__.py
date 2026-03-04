from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.task import Base, Task, IPMapping, TaskLocation
import os

# 数据库路径
DATABASE_PATH = os.getenv("DATABASE_PATH", "database/todo.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# 创建引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite需要
)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库"""
    # 确保数据库目录存在
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def drop_all_tables():
    """删除所有表（用于测试清理）"""
    Base.metadata.drop_all(bind=engine)


__all__ = ["engine", "SessionLocal", "init_db", "get_db", "drop_all_tables", "Task", "IPMapping", "TaskLocation"]
