import reflex as rx
import enum
from typing import Optional, TypedDict
from sqlmodel import Field, SQLModel


class UserRole(str, enum.Enum):
    COMMON_USER = "common_user"
    MANAGER = "manager"


class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    COMPLETED = "completed"


class User(TypedDict):
    id: int
    email: str
    password_hash: str
    role: str


class MedicalRequest(TypedDict):
    id: int
    patient_name: str
    patient_age: int
    patient_gender: str
    patient_id_number: str
    symptoms: str
    diagnosis: str
    medications: str
    medical_history: str
    created_at: str
    status: str
    user_id: int
    documents: str


class SQLModelUser(SQLModel, table=True):
    __tablename__ = "sqlmodeluser"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: str


class MedicalRequest(SQLModel, table=True):
    __tablename__ = "medicalrequest"
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_name: str
    patient_age: int
    patient_gender: str
    patient_id_number: str
    symptoms: str
    diagnosis: str = ""
    medications: str = ""
    medical_history: str = ""
    created_at: str
    status: str
    user_id: int = Field(foreign_key="sqlmodeluser.id")
    documents: str = ""