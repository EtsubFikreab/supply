from fastapi import Depends, HTTPException, Form
from typing import Annotated
from fastapi.routing import APIRouter
from sqlmodel import select, Session

from auth import get_current_user
from db import get_session
from model.organization import Organization
from model.product import Product
from model.warehouse import Warehouse

SessionDep = Annotated[Session, Depends(get_session)]
UserDep = Annotated[dict, Depends(get_current_user)]

admin_router = ar = APIRouter()


@ar.post("/create_organization")
async def create_organization_by_admin(session: SessionDep, current_user: UserDep, new_organization: Organization = Form(...)):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to create an organization.")
    try:
        new_organization.user_id = current_user.get("sub")
        new_organization.id = None
        session.add(new_organization)
        session.commit()
        session.refresh(new_organization)
        return new_organization
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@ar.post("/update_organization", description="Organization ID and User ID will be fetched from the JWT token by default")
async def update_organization_by_admin(session: SessionDep, current_user: UserDep, new_organization: Organization = Form(...)):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to create an organization.")
    try:
        db_organization = session.exec(select(Organization).where(
            Organization.id ==current_user.get("user_metadata").get("organization_id"))).first()
        if not db_organization:
            return HTTPException(status_code=400, detail="Organization does not exist.")

        db_organization.org_name = new_organization.org_name
        db_organization.address = new_organization.address
        db_organization.phone_number = new_organization.phone_number
        db_organization.email = new_organization.email
        db_organization.website = new_organization.website
        db_organization.updated_at = new_organization.updated_at

        session.add(db_organization)
        session.commit()
        session.refresh(db_organization)
        return db_organization
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@ar.delete("/delete_organization")
async def delete_organization_by_admin(session: SessionDep, current_user: UserDep, organization_id):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to delete an organization.")
    try:
        db_organization = session.exec(select(Organization).where(
            Organization.id == organization_id)).first()
        if not db_organization:
            return HTTPException(status_code=400, detail="Organization does not exist.")
        session.delete(db_organization)
        session.commit()
        return {"message": "Organization deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@ar.post("/create_product", description="Organization ID and User ID will be fetched from the JWT token by default, Product ID will also be changed to null by default")
async def create_product(session: SessionDep, current_user: UserDep, new_product: Product = Form(...)):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to create a product.")
    try:
        # if not set to none, cause error with the id autogenerate and foreign key constraints
        new_product.id = None
        if new_product.warehouse_id == "":
            new_product.warehouse_id = None

        if current_user.get("user_metadata").get("organization_id") == "":
            raise HTTPException(
                status_code=400, detail="User does not have an organization_id")

        new_product.organization_id = current_user.get("user_metadata").get("organization_id")
        new_product.user_id = current_user.get("sub")
        session.add(new_product)
        session.commit()
        session.refresh(new_product)

        return new_product

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@ar.post("/update_product", description="Organization ID and User ID will be fetched from the JWT token by default")
async def update_product(session: SessionDep, current_user: UserDep, new_product: Product = Form(...)):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to update a product.")
    db_product = session.exec(select(Product).where(Product.id == new_product.id).where(
        Product.organization_id == current_user.get("user_metadata").get("organization_id"))).first()
    if not db_product:
        return HTTPException(status_code=400, detail="Product does not exist.")
    try:
        if new_product.warehouse_id == "":
            new_product.warehouse_id = None
        db_product.name = new_product.name
        db_product.quantity = new_product.quantity
        db_product.unit_of_measurement = new_product.unit_of_measurement
        db_product.weight = new_product.weight
        db_product.dimensions = new_product.dimensions
        db_product.location = new_product.location
        db_product.batch_number = new_product.batch_number
        db_product.origin = new_product.origin
        db_product.warehouse_id = new_product.warehouse_id
        db_product.cost_price = new_product.cost_price
        db_product.sales_price = new_product.sales_price
        db_product.updated_at = new_product.updated_at
        session.add(db_product)
        session.commit()
        session.refresh(db_product)
        return db_product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@ar.delete("/delete_product", description="Organization ID and User ID will be fetched from the JWT token by default")
async def delete_product(session: SessionDep, current_user: UserDep, product_id: int):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to delete a product.")
    db_product = session.exec(select(Product).where(Product.id == product_id).where(
        Product.organization_id == current_user.get("user_metadata").get("organization_id"))).first()
    if not db_product:
        return HTTPException(status_code=400, detail="Product does not exist.")
    try:
        session.delete(db_product)
        session.commit()
        return {"message": "Product deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@ar.post("/create_warehouse", description="Organization ID and User ID will be fetched from the JWT token by default, Warehouse ID will also be changed to null by default")
async def create_warehouse(session: SessionDep, current_user: UserDep, new_warehouse: Warehouse = Form(...)):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to create a warehouse.")
    try:
        new_warehouse.id = None
        if current_user.get("user_metadata").get("organization_id") == "":
            raise HTTPException(
                status_code=400, detail="User does not have an organization_id")

        new_warehouse.organization_id = current_user.get("user_metadata").get("organization_id")
        new_warehouse.user_id = current_user.get("sub")
        session.add(new_warehouse)
        session.commit()
        session.refresh(new_warehouse)

        return new_warehouse

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@ar.post("/update_warehouse", description="Organization ID and User ID will be fetched from the JWT token by default")
async def update_warehouse(session: SessionDep, current_user: UserDep, new_warehouse: Warehouse = Form(...)):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to update a warehouse.")
    db_warehouse = session.exec(select(Warehouse).where(Warehouse.id == new_warehouse.id).where(
        Warehouse.organization_id == current_user.get("user_metadata").get("organization_id"))).first()
    if not db_warehouse:
        return HTTPException(status_code=400, detail="Warehouse does not exist.")
    try:
        db_warehouse.name = new_warehouse.name
        db_warehouse.longitude = new_warehouse.longitude
        db_warehouse.latitude = new_warehouse.latitude
        db_warehouse.updated_at = new_warehouse.updated_at
        session.add(db_warehouse)
        session.commit()
        session.refresh(db_warehouse)
        return db_warehouse
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@ar.delete("/delete_warehouse")
async def delete_warehouse(session: SessionDep, current_user: UserDep, warehouse_id: int):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to delete a warehouse.")
    db_warehouse = session.exec(select(Warehouse).where(
        Warehouse.id == warehouse_id)).first()
    if not db_warehouse:
        return HTTPException(status_code=400, detail="Warehouse does not exist.")
    try:
        session.delete(db_warehouse)
        session.commit()
        return {"message": "Warehouse deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))