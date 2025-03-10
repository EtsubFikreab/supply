from datetime import datetime

from fastapi import Depends, HTTPException, Form
from typing import Annotated
from fastapi.routing import APIRouter
from sqlmodel import select, Session

from auth import get_current_user
from db import get_session
from model.delivery import Delivery
from model.orders import Transaction, Order
from model.organization import UserOrganization
from model.product import Product
from model.user import Driver
from model.rfq import RFQ, Quotation
from model.warehouse import Warehouse

SessionDep = Annotated[Session, Depends(get_session)]
UserDep = Annotated[dict, Depends(get_current_user)]

dashboard_router = dr = APIRouter()


@dr.get("/total_revenue")
async def get_total_revenue(session: SessionDep, current_user: UserDep):
    if current_user.get("user_role") not in ["admin"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view sales")
    transactions = session.exec(select(Transaction).where(
        Transaction.organization_id == current_user.get("user_metadata").get("organization_id"))).all()
    total_revenue = 0.0
    for transaction in transactions:
        total_revenue += transaction.payment_amount
    return total_revenue


@dr.get("/total_drivers")
async def get_total_drivers(session: SessionDep, current_user: UserDep):
    if current_user.get("user_role") not in ["admin"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view sales")
    drivers = session.exec(select(Driver).distinct()
                           .join(UserOrganization)
                           .where(Driver.driver_id == UserOrganization.user_id)
                           .where(
        UserOrganization.organization_id == current_user.get("user_metadata").get("organization_id"))).all()
    return len(drivers)


@dr.get("/total_orders")
async def get_total_orders(session: SessionDep, current_user: UserDep):
    if current_user.get("user_role") not in ["admin"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view sales")
    orders = session.exec(select(Order).where(
        Order.organization_id == current_user.get("user_metadata").get("organization_id"))).all()
    return len(orders)


@dr.get("/total_shipments")
async def get_total_shipments(session: SessionDep, current_user: UserDep):
    if current_user.get("user_role") not in ["admin"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view sales")
    shipments = session.exec(select(Delivery).where(
        Delivery.organization_id == current_user.get("user_metadata").get("organization_id"))).all()
    return len(shipments)


@dr.get("/total_shipments_today")
async def get_total_shipments_that_were_made_today(session: SessionDep, current_user: UserDep):
    if current_user.get("user_role") not in ["admin"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view sales")
    shipments = session.exec(
        select(Delivery)
        .where(Delivery.organization_id == current_user.get("user_metadata").get("organization_id"))
    ).all()
    today = datetime.now().date()
    today_shipments = []
    for shipment in shipments:
        if shipment.delivered_at and shipment.delivered_at.date() == today:
            today_shipments.append(shipment)
    return len(today_shipments)


@dr.get("/total_orders_today")
async def get_total_orders_that_were_made_today(session: SessionDep, current_user: UserDep):
    if current_user.get("user_role") not in ["admin"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view sales")
    orders = session.exec(select(Order).where(
        Order.organization_id == current_user.get("user_metadata").get("organization_id"))).all()
    today = datetime.now().date()
    today_orders = []
    for order in orders:
        if order.order_date.date() == today:
            today_orders.append(order)
    return len(today_orders)


@dr.get("/total_products")
async def get_total_products(session: SessionDep, current_user: UserDep):
    if current_user.get("user_role") not in ["admin"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view sales")
    products = session.exec(select(Product).where(
        Product.organization_id == current_user.get("user_metadata").get("organization_id"))).all()
    return len(products)


@dr.get("/total_warehouse")
async def get_total_products(session: SessionDep, current_user: UserDep):
    if current_user.get("user_role") not in ["admin"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view sales")
    products = session.exec(select(Warehouse).where(
        Warehouse.organization_id == current_user.get("user_metadata").get("organization_id"))).all()
    return len(products)


@dr.get("/total_expense")
async def get_total_expense(session: SessionDep, current_user: UserDep):
    if current_user.get("user_role") not in ["admin"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view sales")
    quotes = session.exec(select(Quotation).where(Quotation.selected == True).join(RFQ).where(
        RFQ.organization_id == current_user.get("user_metadata").get("organization_id"))).all()
    total_expense = 0.0
    for quote in quotes:
        total_expense += quote.price*quote.quantity
    return total_expense
