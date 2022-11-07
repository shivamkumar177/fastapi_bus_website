from bson import ObjectId
from pydantic import BaseModel, Field
from datetime import datetime

class Cities(BaseModel):
    name: str
    state: str
    class Config:
        arbitrary_types_allowed = True

class showCities(Cities):
    date: str
    number_of_seats_available: int    
class User(BaseModel):
    user_id: str = Field(..., alias='_id') 
    full_name: str
    email: str
    role: str
    hashed_password: str

class BookingDetails(BaseModel):
    booking_id: str = Field(..., alias='_id')
    city_name: str
    date_of_booking : datetime
    date_of_departure: datetime
    Number_of_seats_booked: int
    user_id: str
    city_id: str
    bus_id: str
    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True

class showBookingDetails(BaseModel):
    booking_id: str = Field(..., alias='_id')
    city_name: str
    date_of_booking : datetime
    date_of_departure: datetime
    Number_of_seats_booked: int
    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True

class createUser(BaseModel):
    full_name: str
    email: str
    password: str