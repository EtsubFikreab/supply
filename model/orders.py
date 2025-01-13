from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

from sqlmodel import SQLModel


class Order(SQLModel, table=True):
    __tablename__ = "order"

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organization.id", default=None)
    client_id: int = Field(foreign_key="client.id", nullable=False)
    user_id: uuid.UUID = Field(foreign_key="user_roles.user_id", default=None)  # User who created the order
    order_date: datetime = Field(default_factory=datetime.utcnow) # e.g., Pending, Dispatched, Delivered
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class OrderItem(SQLModel, table=True):
    __tablename__ = "order_item"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", nullable=False)
    product_id: int = Field(foreign_key="product.id", nullable=False)
    quantity: float = Field(nullable=False)
    price: float = Field(nullable=False)

class Invoice:
    order_details: Order
    order_items: OrderItem
    total: float