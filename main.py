from fastapi import FastAPI
from app.routers import booking

app = FastAPI()

app.include_router(booking.router)