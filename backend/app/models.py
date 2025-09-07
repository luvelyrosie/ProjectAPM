from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timezone


class User(Base):
    __tablename__="users"
    
    id=Column(Integer, primary_key=True, index=True)
    username=Column(String, index=True, unique=True, nullable=False)
    email=Column(String, index=True, unique=True, nullable=False)
    role=Column(String, default="operator")
    hashed_password=Column(String)
    
    tasks = relationship("Task", back_populates="operator")
    

class Order(Base):
    __tablename__="orders"
    
    id=Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    status = Column(String, default="Готово к работе")
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)

    tasks = relationship("Task", back_populates="order")
    files = relationship("OrderFile", back_populates="order")
    
    
class OrderFile(Base):
    __tablename__ = "order_files"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)

    order = relationship("Order", back_populates="files")
    

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name= Column(String, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    workstation_id = Column(Integer, ForeignKey("workstations.id"))
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    status = Column(String, default="Готово к работе")
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)

    reject_reason_id = Column(Integer, ForeignKey("reject_reasons.id"), nullable=True)

    order = relationship("Order", back_populates="tasks")
    workstation = relationship("Workstation", back_populates="tasks")
    operator = relationship("User", back_populates="tasks")
    reject_reason = relationship("RejectReason", back_populates="tasks")
    
    
class Workstation(Base):
    __tablename__ = "workstations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)

    tasks = relationship("Task", back_populates="workstation")
    maintenance_logs = relationship("MaintenanceLog", back_populates="workstation")
    
    
class RejectReason(Base):
    __tablename__ = "reject_reasons"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)

    tasks = relationship("Task", back_populates="reject_reason")



class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True)
    workstation_id = Column(Integer, ForeignKey("workstations.id"))
    type = Column(String, nullable=False) 
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    workstation = relationship("Workstation", back_populates="maintenance_logs")
    
    
class Performance(Base):
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    points = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))