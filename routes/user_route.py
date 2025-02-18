from fastapi import Depends, HTTPException, Form
from typing import Annotated
from fastapi.routing import APIRouter
from sqlmodel import select, Session

from auth import get_current_user
from db import get_session
from model.user import Supplier, Client, Driver
from model.organization import UserOrganization

SessionDep = Annotated[Session, Depends(get_session)]
UserDep = Annotated[dict, Depends(get_current_user)]

user_router = ur = APIRouter()


@ur.post("/create_supplier")
async def create_supplier(session: SessionDep, current_user: UserDep, new_supplier: Supplier = Form(...)):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to create a warehouse.")
    try:
        new_supplier.id = None
        if current_user.get("user_metadata").get("organization_id") == "":
            raise HTTPException(
                status_code=400, detail="User does not have an organization_id")
        if new_supplier.user_id == "":
            new_supplier.user_id = None
        session.add(new_supplier)
        session.commit()
        session.refresh(new_supplier)

        return new_supplier

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@ur.get("/suppliers")
async def get_suppliers(session: SessionDep, current_user: UserDep):
    if current_user.get("user_role") not in ["admin", "procurement"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view suppliers.")
    return session.exec(
        select(Supplier)
        .distinct()
        .join(UserOrganization)
        .where(Supplier.user_id == UserOrganization.user_id)
        .where(
            UserOrganization.organization_id == current_user.get("user_metadata").get("organization_id"))).all()


@ur.get("/supplier_by_id")
async def get_supplier_by_id(session: SessionDep, current_user: UserDep, supplier_id: int):
    if current_user.get("user_role") not in ["admin", "procurement"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view suppliers.")
    return session.exec(select(Supplier).where(Supplier.id == supplier_id)).first()


@ur.post("/update_supplier")
async def update_supplier(session: SessionDep, current_user: UserDep, new_supplier: Supplier = Form(...)):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to update a supplier.")
    db_supplier = session.exec(select(Supplier).where(
        Supplier.id == new_supplier.id)).first()
    if not db_supplier:
        return HTTPException(status_code=400, detail="Supplier does not exist.")
    try:
        db_supplier.company_name = new_supplier.company_name
        db_supplier.contact_person_name = new_supplier.contact_person_name
        db_supplier.email = new_supplier.email
        db_supplier.phone = new_supplier.phone

        session.add(db_supplier)
        session.commit()
        session.refresh(db_supplier)
        return db_supplier
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@ur.delete("/delete_supplier")
async def delete_supplier(session: SessionDep, current_user: UserDep, supplier_id: int):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to delete a supplier.")
    db_supplier = session.exec(select(Supplier).where(
        Supplier.id == supplier_id)).first()
    if not db_supplier:
        return HTTPException(status_code=400, detail="Supplier does not exist.")
    try:
        session.delete(db_supplier)
        session.commit()
        return {"message": "Supplier deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@ur.get("/supplier_name")
async def search_supplier_by_name(session: SessionDep, current_user: UserDep, supplier_name: str):
    if current_user.get("user_role") not in ["admin", "procurement"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view suppliers.")
    return session.exec(select(Supplier).where(Supplier.company_name.ilike(f"%{supplier_name}%"))).all()


@ur.post("/create_client")
async def create_client(session: SessionDep, current_user: UserDep, new_client: Client = Form(...)):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to create a warehouse.")
    try:
        new_client.id = None
        new_client.organization_id = current_user.get(
            "user_metadata").get("organization_id")
        session.add(new_client)
        session.commit()
        session.refresh(new_client)

        return new_client

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@ur.get("/clients")
async def get_clients(session: SessionDep, current_user: UserDep):
    if current_user.get("user_role") not in ["admin", "sales"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view clients.")
    return session.exec(select(Client).where(
        Client.organization_id == current_user.get("user_metadata").get("organization_id"))).all()


@ur.get("/client_by_id")
async def get_client_by_id(session: SessionDep, current_user: UserDep, client_id: int):
    if current_user.get("user_role") not in ["admin", "sales"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view clients.")
    return session.exec(select(Client).where(Client.id == client_id)).first()


@ur.post("/update_client")
async def update_client(session: SessionDep, current_user: UserDep, new_client: Client = Form(...)):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to update a client.")
    db_client = session.exec(select(Client).where(
        Client.id == new_client.id)).first()
    if not db_client:
        return HTTPException(status_code=400, detail="Client does not exist.")
    try:
        db_client.company_name = new_client.company_name
        db_client.contact_person = new_client.contact_person
        db_client.email = new_client.email
        db_client.phone = new_client.phone

        session.add(db_client)
        session.commit()
        session.refresh(db_client)
        return db_client
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@ur.delete("/delete_client")
async def delete_client(session: SessionDep, current_user: UserDep, client_id: int):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to delete a client.")
    db_client = session.exec(select(Client).where(
        Client.id == client_id)).first()
    if not db_client:
        return HTTPException(status_code=400, detail="Client does not exist.")
    try:
        session.delete(db_client)
        session.commit()
        return {"message": "Client deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@ur.get("/driver")
async def get_drivers(session: SessionDep, current_user: UserDep):
    if current_user.get("user_role") not in ["admin", "delivery"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view drivers.")
    return session.exec(select(Driver).distinct()
                        .join(UserOrganization)
                        .where(Driver.driver_id == UserOrganization.user_id)
                        .where(
        UserOrganization.organization_id == current_user.get("user_metadata").get("organization_id"))).all()


@ur.get("/driver_by_id")
async def get_driver_by_id(session: SessionDep, current_user: UserDep, driver_id: int):
    if current_user.get("user_role") not in ["admin", "delivery"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view drivers.")
    return session.exec(select(Driver).where(Driver.id == driver_id).where(
        Driver.organization_id == current_user.get("user_metadata").get("organization_id"))).first()


@ur.get("/driver_by_userid")
async def get_driver_by_id(session: SessionDep, current_user: UserDep, user_id: int):
    if current_user.get("user_role") not in ["admin", "delivery"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view drivers.")
    return session.exec(select(Driver).where(Driver.driver_id == user_id).where(
        Driver.organization_id == current_user.get("user_metadata").get("organization_id"))).first()


@ur.post("/create_driver")
async def create_driver(session: SessionDep, current_user: UserDep, new_driver: Driver = Form(...)):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to create a driver.")
    try:
        new_driver.id = None
        session.add(new_driver)
        session.commit()
        session.refresh(new_driver)
        return new_driver

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@ur.post("/update_driver")
async def update_driver(session: SessionDep, current_user: UserDep, new_driver: Driver = Form(...)):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to update a driver.")
    db_driver = session.exec(select(Driver).where(
        Driver.driver_id == new_driver.driver_id)).first()
    if not db_driver:
        return HTTPException(status_code=400, detail="Driver does not exist.")
    try:
        db_driver.name = new_driver.name
        db_driver.car_license_plate = new_driver.car_license_plate
        db_driver.driver_license_id = new_driver.driver_license_id
        db_driver.email = new_driver.email
        db_driver.phone = new_driver.phone

        session.add(db_driver)
        session.commit()
        session.refresh(db_driver)
        return db_driver
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@ur.delete("/delete_driver")
async def delete_driver(session: SessionDep, current_user: UserDep, driver_id: int):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to delete a driver.")
    db_driver = session.exec(select(Driver).where(
        Driver.id == driver_id)).first()
    if not db_driver:
        return HTTPException(status_code=400, detail="Driver does not exist.")
    try:
        session.delete(db_driver)
        session.commit()
        return {"message": "Driver deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@ur.delete("/delete_driver_userid")
async def delete_driver(session: SessionDep, current_user: UserDep, driver_id: int):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to delete a driver.")
    db_driver = session.exec(select(Driver).where(
        Driver.driver_id == driver_id)).first()
    if not db_driver:
        return HTTPException(status_code=400, detail="Driver does not exist.")
    try:
        session.delete(db_driver)
        session.commit()
        return {"message": "Driver deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
