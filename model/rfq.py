from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid
#Request for quotation
class RFQ(SQLModel, table=True):
    __tablename__ = "rfq"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_by: uuid.UUID = Field(foreign_key="user_roles.user_id", nullable=False)
    organization_id: int = Field(foreign_key="organization.id", nullable=False)
    product_id: int = Field(foreign_key="product.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    description: str = Field(max_length=500)
    status: str = Field(max_length=50, default="Open")

class Quotation(SQLModel, table=True):
    __tablename__ = "quotation"

    id: Optional[int] = Field(default=None, primary_key=True)
    supplier_id: uuid.UUID = Field(foreign_key="supplier.supplier_id", nullable=False)
    rfq_id: int = Field(foreign_key="rfq.rfq_id", nullable=False)
    price: float = Field(nullable=False)
    quantity: float = Field(nullable=False)
    selected: bool = Field(default=False)
    delivery_time: int = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)