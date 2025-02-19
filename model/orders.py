from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

from sqlmodel import SQLModel

from model.user import Client


class Order(SQLModel, table=True):
    __tablename__ = "order"

    id: Optional[int] = Field(default=None, primary_key=True)
    # User who created the order
    user_id: uuid.UUID = Field(foreign_key="user_roles.user_id", default=None)
    organization_id: int = Field(foreign_key="organization.id", default=None)
    client_id: int = Field(foreign_key="client.id", nullable=False)
    # e.g., Pending, Dispatched, Delivered
    order_date: datetime = Field(default_factory=datetime.utcnow)
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


class Transaction(SQLModel, table=True):
    __tablename__ = "transaction"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", nullable=False)
    time: datetime = Field(default_factory=datetime.utcnow)
    payment_amount: float = Field(default=0)
    payment_method: str = Field(nullable=False)
    organization_id: int = Field(foreign_key="organization.id", default=None)
