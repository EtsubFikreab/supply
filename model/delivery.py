from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

# Delivery Model
class Delivery(SQLModel, table=True):
    __tablename__ = "delivery"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", nullable=False)
    organization_id: int = Field(foreign_key="organization.id", default=None)
    created_by: Optional[uuid.UUID] = Field(foreign_key="user_roles.user_id", default=None)  # Foreign key to auth.users
    driver_id: Optional[int] = Field(foreign_key="driver.id", default=None)
    destination_longitude: Optional[float] = Field(default=None)
    destination_latitude: Optional[float] = Field(default=None)
    delivery_instructions: Optional[str] = Field(default=None, max_length=255)  # Delivery instructions 
    started_at: datetime = Field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = Field(default=None)
    client_signature: Optional[str] = Field(default=None)  # Optional file path or base64-encoded signature

class DeliveryStatusUpdate(SQLModel, table=True):
    __tablename__ = "delivery_status_update"

    id: Optional[int] = Field(default=None, primary_key=True)
    delivery_id: int = Field(foreign_key="delivery.id", nullable=False)
    delivery_status: str = Field(max_length=50, default="Pending")  # E.g., Pending, Picked Up, Delivered
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = Field(default=None)  # Optional notes

class GPSCoordinates(SQLModel, table=True):
    __tablename__ = "gps_coordinates"

    id: Optional[int] = Field(default=None, primary_key=True)
    delivery_status_id: int = Field(foreign_key="delivery_status_update.id", nullable=False)
    latitude: float = Field(nullable=False)  # Latitude for GPS tracking
    longitude: float = Field(nullable=False)  # Longitude for GPS tracking
    timestamp: datetime = Field(default_factory=datetime.utcnow)