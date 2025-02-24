from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid
# Request for quotation


class RFQ(SQLModel, table=True):
    __tablename__ = "rfq"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_by: Optional[uuid.UUID] = Field(
        foreign_key="user_roles.user_id", default=None)
    organization_id: Optional[int] = Field(
        foreign_key="organization.id", default=None)
    product_id: int = Field(foreign_key="product.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    required_quantity: float = Field(nullable=False)
    description: Optional[str] = Field(max_length=500, default=None)
    status: str = Field(max_length=50, default="Open")


class Quotation(SQLModel, table=True):
    __tablename__ = "quotation"

    id: Optional[int] = Field(default=None, primary_key=True)
    supplier_id: Optional[int] = Field(
        foreign_key="supplier.id", nullable=False)
    rfq_id: int = Field(foreign_key="rfq.id", nullable=False)
    price: Optional[float] = Field(default=None)
    quantity: Optional[float] = Field(default=None)
    selected: bool = Field(default=False)
    delivery_date: Optional[datetime] = Field(
        default_factory=datetime.utcnow, default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[uuid.UUID] = Field(
        foreign_key="user_roles.user_id", default=None)
