import uuid
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from model.warehouse import Warehouse

class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, nullable=False)
    quantity: float = Field(default=0.0)
    unit_of_measurement: str = Field(default=None)
    weight: Optional[float] = Field(default=None)  # in kilograms
    dimensions: Optional[str] = Field(default=None)  # Stored as "Width x Height x Length"
    location: Optional[str] = Field(default=None)  # Location in warehouse
    batch_number: Optional[str] = Field(default=None, max_length=50)
    origin: Optional[str] = Field(default=None, max_length=255)  # Where the item was purchased
    warehouse_id: Optional[int] = Field(foreign_key="warehouse.id", default=None)
    user_id: Optional[uuid.UUID] = Field(foreign_key="user_roles.user_id", default=None)
    organization_id: Optional[int] = Field(foreign_key="organization.id", default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)