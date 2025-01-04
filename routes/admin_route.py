from fastapi import Depends, HTTPException, Form
from typing import Annotated
from fastapi.routing import APIRouter
from sqlmodel import select, Session

from auth import get_current_user
from db import get_session
from model.organization import Organization

SessionDep = Annotated[Session, Depends(get_session)]

admin_routes = ar = APIRouter()

@ar.post("/admin/get_organization")
async def get_user_organization(session: SessionDep, current_user: dict = Depends(get_current_user)):
    user_organization_id = current_user.get("organization_id")
    organizations = session.exec(select(Organization).where(Organization.id == user_organization_id)).all()
    if not organizations:
        return  HTTPException(status_code=400, detail="The organization associated with this user does not exist. Please ensure you have a valid organization.")
    return organizations

@ar.post("/admin/create_organization")
async def create_organization_by_admin(session: SessionDep, current_user: dict = Depends(get_current_user), new_organization: Organization = Form(...)):
    if current_user.get("user_role") != "admin":
        return HTTPException(status_code=400, detail="You do not have the required permissions to create an organization.")
    session.add(new_organization)
    session.commit()
    session.refresh(new_organization)
    return new_organization
