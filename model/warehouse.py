from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field
import uuid


class Warehouse(SQLModel, table=True):
    __tablename__ = "warehouse"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, nullable=False)
    organization_id: Optional[int] = Field(
        foreign_key="organization.id", default=None)
    user_id: Optional[uuid.UUID] = Field(
        foreign_key="user_roles.user_id", default=None)  # user who created the warehouse
    longitude: Optional[float] = Field(default=None)
    latitude: Optional[float] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
