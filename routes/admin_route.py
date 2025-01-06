from fastapi import Depends, HTTPException, Form
from typing import Annotated
from fastapi.routing import APIRouter
from sqlmodel import select, Session

from auth import get_current_user
from db import get_session
from model.organization import Organization
from model.product import Product

SessionDep = Annotated[Session, Depends(get_session)]
UserDep = Annotated[dict, Depends(get_current_user)]

admin_routes = ar = APIRouter()

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
        db_organization = session.exec(select(Organization).where(Organization.id == current_user.get("organization_id"))).first()
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

@ar.post("/create_product", description="Organization ID and User ID will be fetched from the JWT token by default")
async def create_product(session: SessionDep, current_user: UserDep, new_product: Product = Form(...)):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to create a product.")
    try:
        # if not set to none, cause error with the id autogenerate and foreign key constraints
        if new_product.id == "":
            new_product.id = None
        if new_product.warehouse_id == "":
            new_product.warehouse_id = None

        if current_user.get("organization_id") == "":
            raise HTTPException(
                status_code=400, detail="User does not have an organization_id")
        else:
            new_product.organization_id = current_user.get("organization_id")
        new_product.user_id = current_user.get("sub")
        session.add(new_product)
        session.commit()
        session.refresh(new_product)
        return new_product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
