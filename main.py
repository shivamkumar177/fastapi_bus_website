from fastapi import FastAPI
from app.routers import booking, authentication, admin

app = FastAPI()

app.include_router(booking.router)
app.include_router(authentication.router)
app.include_router(admin.router)