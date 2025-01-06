from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

# Delivery Model
class Delivery(SQLModel, table=True):
    __tablename__ = "delivery"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.order_id", nullable=False)
    driver_id: uuid.UUID = Field(foreign_key="driver.driver_id", nullable=False)
    delivery_status: str = Field(max_length=50, default="Pending")  # E.g., Pending, Picked Up, Delivered
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    client_signature: Optional[str] = Field(default=None)  # Optional file path or base64-encoded signature

class DeliveryStatus(SQLModel, table=True):
    __tablename__ = "delivery_status"

    id: Optional[int] = Field(default=None, primary_key=True)
    delivery_id: int = Field(foreign_key="delivery.id", nullable=False)
    status: str = Field(max_length=50)  # E.g., In Transit, Delayed, Delivered
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    location_id: Optional[int] = Field(foreign_key="gps_coordinates.id", default=None)  # Reference to GPS coordinates

class GPSCoordinates(SQLModel, table=True):
    __tablename__ = "gps_coordinates"

    id: Optional[int] = Field(default=None, primary_key=True)
    delivery_id: int = Field(foreign_key="delivery.id", nullable=False)
    latitude: float = Field(nullable=False)  # Latitude for GPS tracking
    longitude: float = Field(nullable=False)  # Longitude for GPS tracking
    location_description: Optional[str] = Field(default=None, max_length=255)  # Optional description of location
