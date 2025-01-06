import uuid
from sqlmodel import SQLModel, Field

class Person:
    name: str = Field(max_length=255, nullable=False)
    email: str = Field(max_length=255, nullable=False)
    phone: str = Field(max_length=15, nullable=False)
    contact_person: str = Field(max_length=255, nullable=False)

class Supplier(Person, SQLModel, table=True):
    __tablename__ = "supplier"

    supplier_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    company_name: str = Field(max_length=255, nullable=False)
    contact_person: str = Field(max_length=255, nullable=False)

class Driver(Person, SQLModel, table=True):
    __tablename__ = "driver"

    driver_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    car_license_plate: str = Field(max_length=15, nullable=False)
    driver_license_id: str = Field(max_length=20, nullable=False)


class Client(Person, SQLModel, table=True):
    __tablename__ = "client"

    company_name: str = Field(max_length=255, nullable=False)
