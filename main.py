from fastapi import FastAPI

from auth import auth_middleware
from routes.admin_route import admin_routes
from routes.auth_route import auth_router
from routes.general_route import general_router
from routes.procurement_route import procurement_routes

app = FastAPI()


app.middleware("http")(auth_middleware)
app.include_router(auth_router, prefix="/auth")
app.include_router(admin_routes, prefix="/admin")
app.include_router(procurement_routes, prefix="/procurement")
app.include_router(general_router)

app.get("/")
def root():
    return {"message": "Hello World"}
