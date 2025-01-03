from fastapi import FastAPI

from auth import auth_middleware
from routes.auth_route import router

app = FastAPI()


app.middleware("http")(auth_middleware)
app.include_router(router)

app.get("/")
def root():
    return {"message": "Hello World"}
