from fastapi import FastAPI

from auth import auth_middleware
from routes.admin_route import admin_routes
from routes.auth_route import auth_router

app = FastAPI()


app.middleware("http")(auth_middleware)
app.include_router(auth_router)
app.include_router(admin_routes)

app.get("/")
def root():
    return {"message": "Hello World"}
