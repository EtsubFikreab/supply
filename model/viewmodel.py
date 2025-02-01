from datetime import datetime

from sqlmodel import Field, SQLModel

from model.orders import Order, OrderItem
from model.user import Client


class Invoice:
    order_details: Order
    order_items: OrderItem
    client_details: Client
    total: float
class ClientOrder(SQLModel, table=False):
    #client detail
    email: str = Field(max_length=255, default=None)
    phone: str = Field(max_length=15, default=None)
    company_name: str = Field(max_length=255, nullable=False)
    contact_person: str = Field(max_length=255, default="CEO")
    client_type: str = Field(max_length=255, default="Shop")

    order_date: datetime = Field(default_factory=datetime.utcnow) # e.g., Pending, Dispatched, Delivered
    