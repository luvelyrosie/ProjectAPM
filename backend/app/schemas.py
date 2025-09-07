from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


# User
class UserRequest(BaseModel):
    username: str = Field(min_length=3)
    email: EmailStr
    role: str 
    password: str = Field(min_length=6)
    
    
class PasswordVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)
    

class Token(BaseModel):
    access_token: str
    token_type: str
    
    
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, description="New username")
    email: Optional[str] = Field(None, description="New email")
    role: Optional[str] = Field(None, description="New role")
    password: Optional[str] = Field(None, description="Current password (required if changing password)")
    new_password: Optional[str] = Field(None, description="New password (required if changing password)")
    

# Order
class OrderBase(BaseModel):
    name: str
    status: Optional[str] = "Готово к работе"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
   
# Task 
class TaskBase(BaseModel):
    name: str
    order_id: int
    workstation_id: int
    operator_id: int
    status: Optional[str] = "Готово к работе"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    reject_reason_id: Optional[int] = None
    
    
class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    name: str
    order_id: Optional[int] = None
    workstation_id: Optional[int] = None
    operator_id: Optional[int] = None
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    reject_reason_id: Optional[int] = None
    
    
class OrderWithTasks(BaseModel):
    id: int
    name: str
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    tasks: List[TaskBase] = []
    

# workstations
class WorkstationBase(BaseModel):
    name: str
    description: Optional[str] = None


class WorkstationCreate(WorkstationBase):
    pass


class WorkstationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    
    
# Reject reasons
class RejectReasonBase(BaseModel):
    description: str


class RejectReasonCreate(RejectReasonBase):
    pass


class RejectReasonUpdate(BaseModel):
    description: str
    
    
# maintenance logs
class MaintenanceLogBase(BaseModel):
    workstation_id: int
    type: str
    description: Optional[str] = None


class MaintenanceLogCreate(MaintenanceLogBase):
    pass


class MaintenanceLogUpdate(BaseModel):
    workstation_id: Optional[int] = None
    type: Optional[str] = None
    description: Optional[str] = None
    
    
# performance
class PerformanceBase(BaseModel):
    user_id: int
    task_id: int
    points: Optional[int] = 1


class PerformanceCreate(PerformanceBase):
    pass


class PerformanceUpdate(BaseModel):
    user_id: Optional[int] = None
    task_id: Optional[int] = None
    points: Optional[int] = None
    
    
class RejectTaskBody(BaseModel):
    reason_id: int