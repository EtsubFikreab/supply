from fastapi import Depends, HTTPException, Form
from typing import Annotated
from fastapi.routing import APIRouter
from sqlmodel import select, Session, or_

from auth import get_current_user
from db import get_session
from model.delivery import Delivery, DeliveryStatusUpdate, GPSCoordinates
from model.orders import Order, OrderItem
from model.product import Product
from model.viewmodel import DeliveryAndStatus

SessionDep = Annotated[Session, Depends(get_session)]
UserDep = Annotated[dict, Depends(get_current_user)]

delivery_router = dr = APIRouter()


@dr.get("/orders_unassigned")
async def get_orders_confirmed_but_not_assigned_to_drivers(session: SessionDep, current_user: UserDep):
    if current_user.get("user_role") not in ["admin", "warehouse", "sales"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view deliveries")
    try:
        return session.exec(select(Order).where(Order.status == "Succeeded").where(
            Order.organization_id == current_user.get("user_metadata").get("organization_id"))).all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@dr.get("/deliveries")
async def get_all_deliveries(session: SessionDep, current_user: UserDep):
    if current_user.get("user_role") not in ["admin", "warehouse", "sales"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view deliveries")
    return session.exec(select(Delivery).where(Delivery.organization_id == current_user.get("user_metadata").get("organization_id"))).all()


@dr.get("/deliveries_driver")
async def get_deliveries_assigned_to_a_specific_driver_used_in_mobile_app(session: SessionDep, current_user: UserDep, driver_id: int):
    if current_user.get("user_role") not in ["admin", "warehouse", "sales", "driver"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view deliveries")
    ready_deliveries = session.exec(select(Delivery).where(Delivery.organization_id == current_user.get("user_metadata").get("organization_id"))
                                    .distinct()
                                    .where(Delivery.driver_id == driver_id)
                                    .join(DeliveryStatusUpdate)
                                    .where(or_(DeliveryStatusUpdate.delivery_status == "Packed", DeliveryStatusUpdate.delivery_status == "In Transit", DeliveryStatusUpdate.delivery_status == "Delayed"))
                                    ).all()
    delivered = session.exec(select(Delivery.id)
                             .where(Delivery.organization_id == current_user.get("user_metadata").get("organization_id"))
                             .where(Delivery.driver_id == driver_id)
                             .join(DeliveryStatusUpdate).where(DeliveryStatusUpdate.delivery_status == "Delivered")).all()
    final = []
    for d in ready_deliveries:
        if d.id not in delivered:
            final.append(d)
    return final


@dr.get("/deliveries_driver_history")
async def get_deliveries_that_a_specific_driver_has_delivered(session: SessionDep, current_user: UserDep, driver_id: int):
    if current_user.get("user_role") not in ["admin", "warehouse", "sales", "driver"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view deliveries")
    return session.exec(select(Delivery)
                        .where(Delivery.organization_id == current_user.get("user_metadata").get("organization_id"))
                        .where(Delivery.driver_id == driver_id)
                        .join(DeliveryStatusUpdate).where(DeliveryStatusUpdate.delivery_status == "Delivered")).all()


@dr.get("/delivery")
async def get_delivery_by_id(session: SessionDep, current_user: UserDep, delivery_id: int):
    if current_user.get("user_role") not in ["admin", "driver", "warehouse", "sales"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view a delivery")
    return session.exec(select(Delivery).where(Delivery.id == delivery_id).where(
        Delivery.organization_id == current_user.get("user_metadata").get("organization_id"))).first()


@dr.get("/delivery_source")
async def get_delivery_by_id(session: SessionDep, current_user: UserDep, delivery_id: int):
    if current_user.get("user_role") not in ["admin", "driver", "warehouse", "sales"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view a delivery")
    return session.exec(select(Delivery).where(Delivery.id == delivery_id).where(
        Delivery.organization_id == current_user.get("user_metadata").get("organization_id"))).first()


@dr.post("/create_delivery")
async def create_delivery(session: SessionDep, current_user: UserDep, new_delivery: Delivery = Form(...)):
    if current_user.get("user_role") not in ["admin", "warehouse"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to create a delivery")
    new_delivery.id = None
    new_delivery.created_by = current_user.get("sub")
    new_delivery.organization_id = current_user.get(
        "user_metadata").get("organization_id")
    session.add(new_delivery)
    session.commit()
    session.refresh(new_delivery)
    return new_delivery


@dr.post("/update_delivery")
async def update_delivery(session: SessionDep, current_user: UserDep, new_delivery: Delivery = Form(...)):
    if current_user.get("user_role") not in ["admin", "warehouse"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to update a delivery")
    db_delivery = session.exec(select(Delivery).where(Delivery.id == new_delivery.id).where(
        Delivery.organization_id == current_user.get("user_metadata").get("organization_id"))).first()
    if not db_delivery:
        return HTTPException(status_code=400, detail="Delivery does not exist.")
    try:
        db_delivery.driver_id = new_delivery.driver_id
        db_delivery.destination_longitude = new_delivery.destination_longitude
        db_delivery.destination_latitude = new_delivery.destination_latitude
        db_delivery.delivery_instructions = new_delivery.delivery_instructions
        db_delivery.destination_name = new_delivery.destination_name
        db_delivery.delivered_at = new_delivery.delivered_at
        db_delivery.client_signature = new_delivery.client_signature

        session.add(db_delivery)
        session.commit()

        if not session.exec(select(DeliveryStatusUpdate).where(DeliveryStatusUpdate.delivery_id == db_delivery.id)).first():
            delivery_status_update: DeliveryStatusUpdate = DeliveryStatusUpdate()
            delivery_status_update.delivery_id = db_delivery.id
            delivery_status_update.delivery_status = "Pending"
            session.add(delivery_status_update)
            session.commit()

        session.refresh(db_delivery)
        return db_delivery
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@dr.delete("/delete_delivery")
async def delete_delivery(session: SessionDep, current_user: UserDep, delivery_id: int = Form(...)):
    if current_user.get("user_role") not in ["admin", "warehouse"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to delete a delivery")
    db_delivery = session.exec(select(Delivery).where(Delivery.id == delivery_id).where(
        Delivery.organization_id == current_user.get("user_metadata").get("organization_id"))).first()
    if not db_delivery:
        return HTTPException(status_code=400, detail="Delivery does not exist.")
    try:
        session.delete(db_delivery)
        session.commit()
        return {"message": "Delivery deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@dr.get("/get_delivery_status_updates")
async def get_delivery_status_updates(session: SessionDep, current_user: UserDep, delivery_id: int):
    if current_user.get("user_role") not in ["admin", "driver", "warehouse", "sales"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view delivery status updates")
    if not session.exec(select(Delivery).where(Delivery.id == delivery_id).where(
            Delivery.organization_id == current_user.get("user_metadata").get("organization_id"))).first():
        return HTTPException(status_code=400, detail="Delivery does not exist.")
    return session.exec(select(DeliveryStatusUpdate).where(DeliveryStatusUpdate.delivery_id == delivery_id).order_by(DeliveryStatusUpdate.timestamp.asc())).all()


@dr.get("/get_latest_delivery_status_update")
async def get_the_latest_delivery_status_update(session: SessionDep, current_user: UserDep, delivery_id: int):
    if current_user.get("user_role") not in ["admin", "driver", "warehouse", "sales"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view delivery status updates")
    if not session.exec(select(Delivery).where(Delivery.id == delivery_id).where(
            Delivery.organization_id == current_user.get("user_metadata").get("organization_id"))).first():
        return HTTPException(status_code=400, detail="Delivery does not exist.")
    return session.exec(select(DeliveryStatusUpdate).where(DeliveryStatusUpdate.delivery_id == delivery_id).order_by(DeliveryStatusUpdate.timestamp.desc())).first()


@dr.post("/create_delivery_status")
async def create_delivery_status_update(session: SessionDep, current_user: UserDep, delivery_status_update: DeliveryStatusUpdate = Form(...)):
    if current_user.get("user_role") not in ["admin", "driver", "warehouse"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to update a delivery")
    try:
        delivery_status_update.id = None
        session.add(delivery_status_update)
        session.commit()
        session.refresh(delivery_status_update)
        return delivery_status_update
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@dr.post("/delivery_packed")
async def status_update_order_is_ready_for_delivery(session: SessionDep, current_user: UserDep, delivery_id: int):
    if current_user.get("user_role") not in ["admin", "driver", "warehouse"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to update a delivery")
    try:
        delivery_status_update: DeliveryStatusUpdate = DeliveryStatusUpdate()
        delivery_status_update.delivery_id = delivery_id
        delivery_status_update.delivery_status = "Packed"
        session.add(delivery_status_update)
        session.commit()

        delivery = session.exec(select(Delivery).where(
            Delivery.id == delivery_id)).first()
        order = session.exec(select(Order).where(
            Order.id == delivery.order_id)).first()
        order_items = session.exec(select(OrderItem).where(
            OrderItem.order_id == order.id)).all()

        for order_item in order_items:
            product = session.exec(select(Product).where(
                Product.id == order_item.product_id)).first()
            product.quantity -= order_item.quantity
            session.add(product)
            session.commit()

        session.refresh(delivery_status_update)
        return delivery_status_update
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@dr.post("/delivery_picked_up")
async def status_update_delivery_is_picked_up_by_the_driver_and_is_in_transit(session: SessionDep, current_user: UserDep, delivery_id: int):
    if current_user.get("user_role") not in ["admin", "driver", "warehouse"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to update a delivery")
    try:
        delivery_status_update: DeliveryStatusUpdate = DeliveryStatusUpdate()
        delivery_status_update.delivery_id = delivery_id
        delivery_status_update.delivery_status = "In Transit"
        session.add(delivery_status_update)
        session.commit()
        session.refresh(delivery_status_update)
        return delivery_status_update
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@dr.post("/delivery_delivered")
async def status_update_delivery_has_arrived_at_its_destination(session: SessionDep, current_user: UserDep, delivery_id: int):
    if current_user.get("user_role") not in ["admin", "driver", "warehouse"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to update a delivery")
    try:
        delivery_status_update: DeliveryStatusUpdate = DeliveryStatusUpdate()
        delivery_status_update.delivery_id = delivery_id
        delivery_status_update.delivery_status = "Delivered"
        session.add(delivery_status_update)
        session.commit()
        session.refresh(delivery_status_update)
        return delivery_status_update
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@dr.post("/delivery_delay")
async def status_update_delivery_has_arrived_at_its_destination(session: SessionDep, current_user: UserDep, delivery_id: int):
    if current_user.get("user_role") not in ["admin", "driver", "warehouse"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to update a delivery")
    try:
        delivery_status_update: DeliveryStatusUpdate = DeliveryStatusUpdate()
        delivery_status_update.delivery_id = delivery_id
        delivery_status_update.delivery_status = "Delayed"
        session.add(delivery_status_update)
        session.commit()
        session.refresh(delivery_status_update)
        return delivery_status_update
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@dr.post("/update_delivery_status")
async def update_delivery_status_update_table_notes(session: SessionDep, current_user: UserDep, delivery_status_update: DeliveryStatusUpdate = Form(...)):
    if current_user.get("user_role") not in ["admin", "driver", "warehouse"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to update a delivery status update")
    db_delivery_status_update = session.exec(select(DeliveryStatusUpdate).where(
        DeliveryStatusUpdate.id == delivery_status_update.id)).first()
    if not db_delivery_status_update:
        return HTTPException(status_code=400, detail="Delivery status update does not exist.")
    try:
        db_delivery_status_update.notes = delivery_status_update.notes

        session.add(db_delivery_status_update)
        session.commit()
        session.refresh(db_delivery_status_update)
        return db_delivery_status_update
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@dr.delete("/delete_delivery_status")
async def delete_delivery_status_update(session: SessionDep, current_user: UserDep, delivery_status_update_id: int = Form(...)):
    if current_user.get("user_role") not in ["admin", "warehouse"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to delete a delivery status update")
    db_delivery_status_update = session.exec(select(DeliveryStatusUpdate).where(
        DeliveryStatusUpdate.id == delivery_status_update_id)).first()
    if not db_delivery_status_update:
        return HTTPException(status_code=400, detail="Delivery status update does not exist.")
    try:
        session.delete(db_delivery_status_update)
        session.commit()
        return {"message": "Delivery status update deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@dr.get("/get_delivery_gps")
async def get_gps_coordinate_of_delivery_that_is_on_route_to_a_client(session: SessionDep, current_user: UserDep, delivery_status_id: int):
    if current_user.get("user_role") not in ["admin", "warehouse", "sales", "driver"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view GPS coordinates")
    return session.exec(select(GPSCoordinates).where(GPSCoordinates.delivery_status_id == delivery_status_id)).all()


@dr.post("/add_gps")
async def create_gps_coordinate_update_this_is_done_by_driver(session: SessionDep, current_user: UserDep, gps: GPSCoordinates = Form(...)):
    if current_user.get("user_role") not in ["admin", "driver", "warehouse"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to create GPS coordinates")
    try:
        gps.id = None
        session.add(gps)
        session.commit()
        session.refresh(gps)
        return gps
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
