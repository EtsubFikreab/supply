from fastapi import FastAPI

from auth import auth_middleware
from routes.admin_route import admin_routes
from routes.auth_route import auth_router
from routes.general_route import general_router
from routes.procurement_route import procurement_router
from routes.sales_route import sales_router

app = FastAPI()


app.middleware("http")(auth_middleware)
app.include_router(auth_router, prefix="/auth")
app.include_router(admin_routes, prefix="/admin")
app.include_router(procurement_router, prefix="/procurement")
app.include_router(general_router)
app.include_router(sales_router, prefix="/sales")

app.get("/")
def root():
    return {"message": "Hello World"}
