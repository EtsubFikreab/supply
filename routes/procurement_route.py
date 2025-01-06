from fastapi import Depends, HTTPException, Form
from typing import Annotated
from fastapi.routing import APIRouter
from sqlmodel import select, Session

from auth import get_current_user
from db import get_session
from model.rfq import RFQ

SessionDep = Annotated[Session, Depends(get_session)]
UserDep = Annotated[dict, Depends(get_current_user)]

procurement_routes = pr = APIRouter()

@pr.get("/rfq")
async def get_request_for_quotation(session: SessionDep, current_user: UserDep):
    if current_user.get("user_role") not in ["admin", "procurement"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to view request for quotation")
    return session.exec(select(RFQ)).all()

@pr.post("/create_rfq")
def create_request_for_quotation(session: SessionDep, current_user: UserDep, new_rfq: RFQ = Form(...)):
    if current_user.get("user_role") not in ["admin", "procurement"]:
        return HTTPException(status_code=400, detail="You do not have the required permissions to create a request for quotation")
    session.add(new_rfq)
    session.commit()
    session.refresh(new_rfq)
    return new_rfq