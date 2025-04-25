from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean,
    TIMESTAMP, Interval, ForeignKey, func
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    username = Column(String(255))
    is_bot_admin = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    tasks = relationship('Task', back_populates='user', cascade='all, delete-orphan')
    comments = relationship('Comment', back_populates='user', cascade='all, delete-orphan')


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    due_date = Column(TIMESTAMP)
    status = Column(String(50), default='pending')

    user = relationship('User', back_populates='tasks')
    comments = relationship('Comment', back_populates='task', cascade='all, delete-orphan')
    time_entries = relationship('TimeEntry', back_populates='task', cascade='all, delete-orphan')


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    task = relationship('Task', back_populates='comments')
    user = relationship('User', back_populates='comments')


class TimeEntry(Base):
    __tablename__ = 'time_entries'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'))
    duration = Column(Interval, nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=False)

    task = relationship('Task', back_populates='time_entries')
