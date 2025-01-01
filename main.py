from fastapi import FastAPI

from auth import auth_middleware
from routes import auth

app = FastAPI()


app.middleware("http")(auth_middleware)
app.include_router(auth.router)

app.get("/")
def root():
    return {"message": "Hello World"}
