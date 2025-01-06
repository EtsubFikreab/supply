from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field
import uuid
class Warehouse(SQLModel, table=True):
    __tablename__ = "warehouse"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, nullable=False)
    organization_id: int = Field(foreign_key="organization.id", nullable=False)
    user_id: uuid.UUID = Field(foreign_key="user_roles.user_id", nullable=False)  #user who created the warehouse
    location: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)