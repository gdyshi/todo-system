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
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


__all__ = ["engine", "SessionLocal", "init_db", "get_db", "Task", "IPMapping", "TaskLocation"]
