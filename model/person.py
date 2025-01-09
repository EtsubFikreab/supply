import uuid
from typing import Optional

from sqlmodel import SQLModel, Field


class Person:
    id: int = Field(default=None, primary_key=True)
    email: str = Field(max_length=255,default=None)
    phone: str = Field(max_length=15, default=None)


class Supplier(Person, SQLModel, table=True):
    __tablename__ = "supplier"

    user_id: Optional[uuid.UUID] = Field(foreign_key="user_roles.user_id", default=None)  # Foreign key to auth.users
    company_name: str = Field(max_length=255, nullable=False)
    contact_person_name: str = Field(max_length=255, default=None)


class Driver(Person, SQLModel, table=True):
    __tablename__ = "driver"

    name: str = Field(max_length=255, nullable=False)
    user_id: Optional[uuid.UUID] = Field(foreign_key="user_roles.user_id", default=None)  # Foreign key to auth.users
    car_license_plate: str = Field(max_length=15, nullable=False)
    driver_license_id: str = Field(max_length=20, nullable=False)


class Client(Person, SQLModel, table=True):
    __tablename__ = "client"

    company_name: str = Field(max_length=255, nullable=False)
    contact_person: str = Field(max_length=255, default="CEO")
