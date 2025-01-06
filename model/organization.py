from datetime import datetime
from sqlmodel import Field, SQLModel
from typing import Optional
import uuid

class Organization(SQLModel, table=True):
    __tablename__ = "organization"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[uuid.UUID] = Field(foreign_key="user_roles.user_id", default=None)  # Foreign key to auth.users
    org_name: str = Field(max_length=255, nullable=False)
    address: Optional[str] = None
    phone_number: Optional[str] = Field(default=None, max_length=15)
    email: Optional[str] = Field(default=None, max_length=255)
    website: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserRoles(SQLModel, table=True):
    __tablename__ = "user_roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="auth.users.id", nullable=False, unique=True)  # Unique foreign key to auth.users
    role: str = Field(nullable=False)