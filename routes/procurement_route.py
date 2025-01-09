import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import Depends, HTTPException, Form
from typing import Annotated
from fastapi.routing import APIRouter
from sqlmodel import select, Session

from auth import get_current_user
from db import get_session
from model.person import Supplier
from model.rfq import RFQ, Quotation

SessionDep = Annotated[Session, Depends(get_session)]
UserDep = Annotated[dict, Depends(get_current_user)]

procurement_router = pr = APIRouter()


@pr.get("/rfq")
async def get_request_for_rfqs(session: SessionDep, current_user: UserDep):
    if current_user.get("user_role") not in ["admin", "procurement", "supplier"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view request for quotation")
    return session.exec(select(RFQ).where(RFQ.organization_id == current_user.get("organization_id"))).all()


@pr.post("/create_rfq")
async def create_request_for_rfq(session: SessionDep, current_user: UserDep, new_rfq: RFQ = Form(...)):
    if current_user.get("user_role") not in ["admin", "procurement"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to create a request for quotation")
    new_rfq.id = None
    new_rfq.created_by = current_user.get("sub")
    new_rfq.organization_id = current_user.get("organization_id")
    session.add(new_rfq)
    session.commit()
    session.refresh(new_rfq)
    return new_rfq


@pr.post("/update_rfq")
async def update_request_for_rfq(session: SessionDep, current_user: UserDep, new_rfq: RFQ = Form(...)):
    if current_user.get("user_role") not in ["admin", "procurement"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to update a request for quotation")
    db_rfq = session.exec(select(RFQ).where(RFQ.id == new_rfq.id).where(
        RFQ.organization_id == current_user.get("organization_id"))).first()
    if not db_rfq:
        return HTTPException(status_code=400, detail="Request for quotation does not exist.")
    try:
        db_rfq.required_quantity = new_rfq.required_quantity
        db_rfq.description = new_rfq.description
        db_rfq.status = new_rfq.status
        db_rfq.product_id = new_rfq.product_id
        db_rfq.status = new_rfq.status

        session.add(db_rfq)
        session.commit()
        session.refresh(db_rfq)
        return db_rfq
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@pr.delete("/delete_rfq")
async def delete_request_for_rfq(session: SessionDep, current_user: UserDep, rfq_id: int):
    if current_user.get("user_role") not in ["admin", "procurement"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to delete a request for quotation")
    db_rfq = session.exec(select(RFQ).where(RFQ.id == rfq_id).where(
        RFQ.organization_id == current_user.get("organization_id"))).first()
    if not db_rfq:
        return HTTPException(status_code=400, detail="Request for quotation does not exist.")

    session.delete(db_rfq)
    session.commit()
    return {"message": "Request for quotation deleted successfully."}


@pr.get("/quotation")
async def get_quotations(session: SessionDep, current_user: UserDep, rfq_id: int):
    if current_user.get("user_role") not in ["admin", "procurement"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view quotations")
    rfq = session.exec(select(RFQ).where(RFQ.id == rfq_id).where(
        RFQ.organization_id == current_user.get("organization_id"))).first()
    if not rfq:
        return HTTPException(status_code=400, detail="RFQ does not exist.")
    return session.exec(select(Quotation).where(Quotation.rfq_id == rfq_id)).all()


@pr.post("/create_quotation")
async def create_quotation(session: SessionDep, current_user: UserDep, new_quotation: Quotation = Form(...)):
    if current_user.get("user_role") not in ["admin", "procurement", "supplier"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to create a quotation")
    try:
        if new_quotation.selected=="true":
            new_quotation.selected = True
        else:
            new_quotation.selected = False
        new_quotation.id = None
        new_quotation.created_by = current_user.get("sub")
        if new_quotation.supplier_id == "":
            new_quotation.supplier_id = None
        session.add(new_quotation)
        session.commit()
        session.refresh(new_quotation)
        return new_quotation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@pr.post("/update_quotation")
async def update_quotation(session: SessionDep, current_user: UserDep, new_quotation: Quotation = Form(...)):
    if current_user.get("user_role") not in ["admin", "procurement", "supplier"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to update a quotation")
    db_quotation = session.exec(select(Quotation).where(Quotation.id == new_quotation.id)).first()
    if not db_quotation:
        return HTTPException(status_code=400, detail="Quotation does not exist.")
    try:
        if new_quotation.selected=="true":
            new_quotation.selected = True
        else:
            new_quotation.selected = False
        db_quotation.price = new_quotation.price
        db_quotation.quantity = new_quotation.quantity
        db_quotation.selected = new_quotation.selected
        db_quotation.delivery_date = new_quotation.delivery_date
        session.add(db_quotation)
        session.commit()
        session.refresh(db_quotation)
        return db_quotation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@pr.delete("/delete_quotation")
async def delete_quotation(session: SessionDep, current_user: UserDep, quotation_id: int):
    if current_user.get("user_role") not in ["admin", "procurement"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to delete a quotation")
    db_quotation = session.exec(select(Quotation).where(Quotation.id == quotation_id)).first()
    if not db_quotation:
        return HTTPException(status_code=400, detail="Quotation does not exist.")
    session.delete(db_quotation)
    session.commit()
    return {"message": "Quotation deleted successfully."}

@pr.post("/select_quotation")
async def select_quotation(session: SessionDep, current_user: UserDep, quotation_id: int):
    if current_user.get("user_role") not in ["admin", "procurement"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to select a quotation")
    try:
        db_quotation = session.exec(select(Quotation).where(Quotation.id == quotation_id)).first()
        if not db_quotation:
            return HTTPException(status_code=400, detail="Quotation does not exist.")
        db_quotation.selected = True
        session.add(db_quotation)
        session.commit()
        session.refresh(db_quotation)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    # Send email to supplier
    try:
        supplier = session.exec(select(Supplier).where(Supplier.id == db_quotation.supplier_id)).first()
        if supplier and supplier.email:
            sender_email = "procurement@supplychain.com"
            receiver_email = supplier.email
            subject = "Quotation Selected"
            body = f"Dear {supplier.company_name},\n\nYour quotation with ID {quotation_id} has been selected.\n\nBest regards,\nYour Company"
            
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))
            
            with smtplib.SMTP("localhost", 587) as server:
                server.starttls()
                server.login(sender_email, "your_password")
                server.sendmail(sender_email, receiver_email, message.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

    return db_quotation