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
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    is_admin = Column(Boolean, server_default='false', nullable=False)  # <--- Новое поле

    tasks = relationship('Task', back_populates='user', cascade='all, delete-orphan')
    comments = relationship('Comment', back_populates='user', cascade='all, delete-orphan')



class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    due_date = Column(TIMESTAMP)

    user = relationship('User', back_populates='tasks')
    status = relationship('Status', back_populates='task', uselist=False, cascade='all, delete-orphan')
    time_entries = relationship('TimeEntry', back_populates='task', cascade='all, delete-orphan')
    comments = relationship('Comment', back_populates='task', cascade='all, delete-orphan')


class Status(Base):
    __tablename__ = 'statuses'

    id = Column(Integer, primary_key=True)
    status = Column(String(50), nullable=False)  # e.g. 'pending', 'in_progress', 'completed'
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False, unique=True)

    task = relationship('Task', back_populates='status')


class TimeEntry(Base):
    __tablename__ = 'time_entries'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    duration = Column(Interval, nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=False)

    task = relationship('Task', back_populates='time_entries')


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    task = relationship('Task', back_populates='comments')
    user = relationship('User', back_populates='comments')
