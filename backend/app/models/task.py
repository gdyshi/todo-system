from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Task(Base):
    """任务模型"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)  # work/life/education
    status = Column(String(50), nullable=False, default="pending")  # pending/in_progress/completed
    parent_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    priority = Column(Integer, default=0)  # 0-9
    due_time = Column(DateTime, nullable=True)
    location = Column(Text, nullable=True)  # JSON格式存储坐标
    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    parent = relationship("Task", remote_side=[id], backref="subtasks")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "status": self.status,
            "parent_id": self.parent_id,
            "priority": self.priority,
            "due_time": self.due_time.isoformat() if self.due_time else None,
            "location": self.location,
            "reminder_sent": self.reminder_sent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "subtasks": [subtask.to_dict() for subtask in self.subtasks] if self.subtasks else []
        }


class IPMapping(Base):
    """IP映射模型"""
    __tablename__ = "ip_mappings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_pattern = Column(String(100), nullable=False, unique=True)
    category = Column(String(50), nullable=False)
    auto = Column(Boolean, default=True)
    manual_override = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "ip_pattern": self.ip_pattern,
            "category": self.category,
            "auto": self.auto,
            "manual_override": self.manual_override,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class TaskLocation(Base):
    """任务位置记录模型"""
    __tablename__ = "task_locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    ip = Column(String(100), nullable=False)
    location = Column(Text, nullable=True)  # JSON格式
    category = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "ip": self.ip,
            "location": self.location,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
