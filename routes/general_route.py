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

general_router = gr = APIRouter()


@gr.get("/get_organization")
async def get_user_organization(session: SessionDep, current_user: UserDep):
    try:
        user_organization_id = current_user.get("organization_id")
        organizations = session.exec(select(Organization).where(
            Organization.id == user_organization_id)).all()
        if not organizations:
            return HTTPException(status_code=400, detail="The organization associated with this user does not exist. Please ensure you have a valid organization.")
        return organizations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@gr.get("/get_products")
async def get_all_products(session: SessionDep, current_user: UserDep):
    try:
        user_organization_id = current_user.get("organization_id")
        products = session.exec(select(Product).where(
            Product.organization_id == user_organization_id)).all()
        return products
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@gr.get("/product_id")
async def get_product_by_id(session: SessionDep, current_user: UserDep, product_id: int):
    try:
        user_organization_id = current_user.get("organization_id")
        products = session.exec(select(Product).where(Product.id == product_id).where(
            Product.organization_id == user_organization_id)).all()
        return products
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@gr.get("/product_name", description="Checks if the search term is in the product name")
async def search_product_by_name(session: SessionDep, current_user: UserDep, product_name: str):
    try:
        user_organization_id = current_user.get("organization_id")
        products = session.exec(
            select(Product)
            .where(Product.name.ilike(f"%{product_name}%"))
            .where(Product.organization_id == user_organization_id)
        ).all()
        return products
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))