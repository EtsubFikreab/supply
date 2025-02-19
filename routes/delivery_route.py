from fastapi import Depends, HTTPException, Form
from typing import Annotated
from fastapi.routing import APIRouter
from sqlmodel import select, Session

from auth import get_current_user
from db import get_session
from model.delivery import Delivery, DeliveryStatusUpdate, GPSCoordinates
from model.orders import Order
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


@dr.get("/deliveries_status")
async def get_all_deliveries_along_with_their_status(session: SessionDep, current_user: UserDep):
    if current_user.get("user_role") not in ["admin", "warehouse", "sales"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view deliveries")
    delivery_and_status = DeliveryAndStatus()
    delivery_and_status.delivery = session.exec(select(Delivery).where(
        Delivery.organization_id == current_user.get("user_metadata").get("organization_id"))).all()
    for ds in delivery_and_status:
        ds.delivery_status = session.exec(select(DeliveryStatusUpdate).where(
            DeliveryStatusUpdate.delivery_id == ds.delivery.id)).all()
    return delivery_and_status


@dr.get("/deliveries_driver")
async def get_deliveries_assigned_to_a_specific_driver_used_in_mobile_app(session: SessionDep, current_user: UserDep, driver_id: int):
    if current_user.get("user_role") not in ["admin", "warehouse", "sales", "driver"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view deliveries")
    return session.exec(select(Delivery).where(Delivery.organization_id == current_user.get("user_metadata").get("organization_id")).where(Delivery.driver_id == driver_id)).all()


@dr.get("/delivery")
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
        db_delivery.delivered_at = new_delivery.delivered_at
        db_delivery.client_signature = new_delivery.client_signature

        session.add(db_delivery)
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
    return session.exec(select(DeliveryStatusUpdate).where(DeliveryStatusUpdate.delivery_id == delivery_id)).all()


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
