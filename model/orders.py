from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

from sqlmodel import SQLModel

from model.user import Client


class Order(SQLModel, table=True):
    __tablename__ = "order"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user_roles.user_id", default=None)  # User who created the order
    organization_id: int = Field(foreign_key="organization.id", default=None)
    client_id: int = Field(foreign_key="client.id", nullable=False)
    order_date: datetime = Field(default_factory=datetime.utcnow) # e.g., Pending, Dispatched, Delivered
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="Pending")

class OrderItem(SQLModel, table=True):
    __tablename__ = "order_item"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", nullable=False)
    product_id: int = Field(foreign_key="product.id", nullable=False)
    quantity: float = Field(nullable=False)
    price: float = Field(nullable=False)