from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

# Delivery Model


class Delivery(SQLModel, table=True):
    __tablename__ = "delivery"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: Optional[int] = Field(foreign_key="order.id")
    organization_id: int = Field(foreign_key="organization.id", default=None)
    created_by: Optional[uuid.UUID] = Field(
        foreign_key="user_roles.user_id", default=None)  # Foreign key to auth.users
    driver_id: Optional[int] = Field(foreign_key="driver.id", default=None)
    destination_longitude: Optional[float] = Field(default=None)
    destination_latitude: Optional[float] = Field(default=None)
    destination_name: Optional[str] = Field(
        default=None, max_length=255)  # Delivery instructions
    delivery_instructions: Optional[str] = Field(
        default=None, max_length=255)  # Delivery instructions
    started_at: datetime = Field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = Field(default=None)
    # Optional file path or base64-encoded signature
    client_signature: Optional[str] = Field(default=None)


class DeliveryStatusUpdate(SQLModel, table=True):
    __tablename__ = "delivery_status_update"

    id: Optional[int] = Field(default=None, primary_key=True)
    delivery_id: int = Field(foreign_key="delivery.id", nullable=False)
    # E.g., Pending, Picked Up, Delivered
    delivery_status: str = Field(max_length=50, default="Pending")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = Field(default=None)  # Optional notes


class GPSCoordinates(SQLModel, table=True):
    __tablename__ = "gps_coordinates"

    id: Optional[int] = Field(default=None, primary_key=True)
    delivery_status_id: int = Field(
        foreign_key="delivery_status_update.id", nullable=False)
    latitude: float = Field(nullable=False)  # Latitude for GPS tracking
    longitude: float = Field(nullable=False)  # Longitude for GPS tracking
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ShipmentDelivery(SQLModel, table=True):
    __tablename__ = "shipment_delivery"

    id: Optional[int] = Field(default=None, primary_key=True)
    source: Optional[str] = Field(default=None, max_length=255)
    warehouse_id: Optional[int] = Field(
        foreign_key="warehouse.id", default=None)
    container_number: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)
    organization_id: Optional[int] = Field(
        foreign_key="organization.id", default=None)
    driver_id: Optional[int] = Field(foreign_key="driver.id", default=None)

class ShipmentTracking(SQLModel, table=True):
    __tablename__ = "shipment_tracking"
    id: Optional[int] = Field(default=None, primary_key=True)
    shipment_delivery_id: Optional[int] = Field(foreign_key="shipment_delivery.id", default=None)
    detail: Optional[str] = Field(default=None, max_length=255)
    latitude: float = Field(nullable=False)  # Latitude for GPS tracking
    longitude: float = Field(nullable=False)  # Longitude for GPS tracking
    