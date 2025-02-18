from datetime import datetime
from sqlmodel import Field, SQLModel
from typing import Optional
import uuid


class Organization(SQLModel, table=True):
    __tablename__ = "organization"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[uuid.UUID] = Field(
        foreign_key="user_roles.user_id", default=None)  # Foreign key to auth.users
    org_name: Optional[str] = Field(max_length=255, default=None)
    address: Optional[str] = None
    phone_number: Optional[str] = Field(default=None, max_length=15)
    email: Optional[str] = Field(default=None, max_length=255)
    website: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserRoles(SQLModel, table=True):
    __tablename__ = "user_roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    # Unique foreign key to auth.users
    user_id: uuid.UUID = Field(
        foreign_key="auth.users.id", nullable=False, unique=True)
    role: str = Field(nullable=False)


class UserOrganization (SQLModel, table=True):
    __tablename__ = "user_organization"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="auth.users.id", nullable=False, unique=True)
    organization_id: Optional[int] = Field(
        foreign_key="organization.id", default=None)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
