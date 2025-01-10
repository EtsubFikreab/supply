from fastapi import Depends, HTTPException, Form
from typing import Annotated
from fastapi.routing import APIRouter
from sqlmodel import select, Session

from auth import get_current_user
from db import get_session
from model.orders import Order, OrderItem

SessionDep = Annotated[Session, Depends(get_session)]
UserDep = Annotated[dict, Depends(get_current_user)]

sales_router = sr = APIRouter()

@sr.get("/orders")
async def get_orders(session: SessionDep, current_user: UserDep):
    if current_user.get("user_role") not in ["admin", "sales"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view sales")
    return session.exec(select(Order).where(Order.organization_id == current_user.get("organization_id"))).all()

@sr.post("/create_order")
async def create_order(session: SessionDep, current_user: UserDep, new_order: Order = Form(...)):
    if current_user.get("user_role") not in ["admin", "sales"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to create a sales order")
    try:
        new_order.id = None
        new_order.user_id = current_user.get("sub")
        new_order.organization_id = current_user.get("organization_id")
        session.add(new_order)
        session.commit()
        session.refresh(new_order)
        return new_order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 

@sr.post("/update_order")
async def update_order(session: SessionDep, current_user: UserDep, new_order: Order = Form(...)):
    if current_user.get("user_role") not in ["admin", "sales"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to update a sales order")
    db_order = session.exec(select(Order).where(Order.id == new_order.id).where(
        Order.organization_id == current_user.get("organization_id"))).first()
    if not db_order:
        return HTTPException(status_code=400, detail="Order does not exist.")
    try:
        db_order.client_id = new_order.client_id
        db_order.order_date = new_order.order_date
        db_order.updated_at = new_order.updated_at

        session.add(db_order)
        session.commit()
        session.refresh(db_order)
        return db_order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@sr.delete("/delete_order")
async def delete_order(session: SessionDep, current_user: UserDep, order_id: int = Form(...)):
    if current_user.get("user_role") not in ["admin", "sales"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to delete a sales order")
    db_order = session.exec(select(Order).where(Order.id == order_id).where(
        Order.organization_id == current_user.get("organization_id"))).first()
    if not db_order:
        return HTTPException(status_code=400, detail="Order does not exist.")
    try:
        session.delete(db_order)
        session.commit()
        return {"message": "Order deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@sr.get("/order_items")
async def get_order_items(session: SessionDep, current_user: UserDep, order_id: int):
    if current_user.get("user_role") not in ["admin", "sales"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view sales order items")
    if not session.exec(select(Order).where(Order.id == order_id).where(Order.organization_id == current_user.get("organization_id"))).first():
        return HTTPException(status_code=400, detail="Order does not exist.")
    return session.exec(select(OrderItem).where(OrderItem.order_id==order_id)).all()

@sr.post("/create_order_item")
async def create_order_item(session: SessionDep, current_user: UserDep, new_order_item: OrderItem = Form(...)):
    if current_user.get("user_role") not in ["admin", "sales"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to create a sales order item")
    if not session.exec(select(Order).where(Order.id == new_order_item.order_id).where(Order.organization_id == current_user.get("organization_id"))).first():
        return HTTPException(status_code=400, detail="Order does not exist.")
    try:
        new_order_item.id = None
        session.add(new_order_item)
        session.commit()
        session.refresh(new_order_item)
        return new_order_item
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@sr.post("/update_order_item")
async def update_order_item(session: SessionDep, current_user: UserDep, new_order_item: OrderItem = Form(...)):
    if current_user.get("user_role") not in ["admin", "sales"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to update a sales order item")
    if not session.exec(select(Order).where(Order.id == new_order_item.order_id).where(Order.organization_id == current_user.get("organization_id"))).first():
        return HTTPException(status_code=400, detail="Order does not exist.")
    db_order_item = session.exec(select(OrderItem).where(OrderItem.id == new_order_item.id).where(
        OrderItem.order_id == new_order_item.order_id)).first()
    if not db_order_item:
        return HTTPException(status_code=400, detail="Order item does not exist.")
    try:
        db_order_item.product_id = new_order_item.product_id
        db_order_item.quantity = new_order_item.quantity
        db_order_item.price = new_order_item.price

        session.add(db_order_item)
        session.commit()
        session.refresh(db_order_item)
        return db_order_item
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@sr.delete("/delete_order_item")
async def delete_order_item(session: SessionDep, current_user: UserDep, order_item_id: int = Form(...)):
    if current_user.get("user_role") not in ["admin", "sales"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to delete a sales order item")
    if not session.exec(select(OrderItem).where(OrderItem.id == order_item_id)).first():
        return HTTPException(status_code=400, detail="Order item does not exist.")
    db_order_item = session.exec(select(OrderItem).where(OrderItem.id == order_item_id)).first()
    if not db_order_item:
        return HTTPException(status_code=400, detail="Order item does not exist.")
    try:
        session.delete(db_order_item)
        session.commit()
        return {"message": "Order item deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))