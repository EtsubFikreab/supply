from fastapi import FastAPI

from auth import auth_middleware
from routes.admin_route import admin_router
from routes.auth_route import auth_router
from routes.dashboard_route import dashboard_router
from routes.delivery_route import delivery_router
from routes.general_route import general_router
from routes.procurement_route import procurement_router
from routes.sales_route import sales_router
from routes.user_route import user_router

app = FastAPI()


app.middleware("http")(auth_middleware)
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(procurement_router, prefix="/procurement", tags=["procurement"])
app.include_router(general_router, tags=["general"])
app.include_router(sales_router, prefix="/sales", tags=["sales"])
app.include_router(delivery_router, prefix="/delivery", tags=["delivery"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])

app.get("/")
def root():
    return {"message": "Hello World"}
