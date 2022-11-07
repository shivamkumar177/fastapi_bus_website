from datetime import datetime
from typing import List
from fastapi import APIRouter, status, HTTPException, Depends
import app.models as models
from app import database, aggergations
from bson import ObjectId
from app import auth

router = APIRouter(
    prefix="/booking",
    tags=["booking"]
)

def objectid_to_string(each_booking):
    each_booking["_id"] = str(each_booking["_id"])
    each_booking["city_id"] = str(each_booking["city_id"])
    each_booking["user_id"] = str(each_booking["user_id"])
    each_booking["bus_id"] = str(each_booking["bus_id"])
    return each_booking

@router.get('/cities', response_model= List[models.Cities], status_code=status.HTTP_200_OK)
def list_all_cities():
    ''' List all cities present
    Arguments:
        None
    Returns:
        List of citiesd
    '''
    data = []
    try:
        data = database.fetch_data("cities",{})
    except Exception as e:
        print(e)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "No cities found!")
    data = [models.Cities(**x) for x in data ]
    return data

@router.get('/{city}/{state}/{book_date}', response_model = models.showCities, status_code=status.HTTP_200_OK)
def get_seat_availability(city: str, book_date: str, state: str):
    ''' Gets seat availaiblity for a particular city on a given date
    Arguments:
        city: str
        book_data: str
    Returns:
        showCities: available seats in a city
    '''
    book_date_obj = datetime.strptime(book_date, "%Y-%m-%d")
    if datetime.today().date()>book_date_obj.date():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Booking date!")
    # return all the cities on date
    # if city == '*':
    #     all_cities_data = []
    #     fetch_all_cities = database.fetch_data("cities", {})
    #     for each_city in fetch_all_cities:
    #         city_id = each_city.get('_id')
    #         bus_id = database.get_bus_id(city_id)
    #         aggregate_query = aggergations.get_available_seats(bus_id, book_date_obj)
    #         print(aggregate_query)
    #         booked_seats = 0
    #         try:
    #             res = database.aggregation("orders", aggregate_query)[0]
    #             booked_seats = res.get('count')
    #         except Exception as e:
    #             print(e)
    #         total_seats_in_bus = database.fetch_data("bus_info", {"_id": ObjectId(bus_id)})[0].get("total_seats")
    #         all_cities_data.append(
    #             models.showCities(name=each_city['name'], date=book_date, number_of_seats_available=total_seats_in_bus-booked_seats, state=each_city['state'])
    #         )
    #     return all_cities_data
    city_id = database.get_city_id(city.lower(), state.lower())
    bus_id = database.get_bus_id(city_id)
    if not bus_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Bus found!")
    bus_seats_booked = 0
    aggregate_query = aggergations.get_available_seats(bus_id, book_date_obj)
    try:
        data = database.aggregation("orders", aggregate_query)[0]
        bus_seats_booked = data.get("count")
    except Exception as e:
        print(e)
    total_seats_in_bus = database.fetch_data("bus_info", {"_id": ObjectId(bus_id)})[0].get("total_seats")
    if total_seats_in_bus-bus_seats_booked == 0:
        return {"message": "No Seats Availabe!"}
    return (models.showCities(name=city, date=book_date, number_of_seats_available=total_seats_in_bus-bus_seats_booked, state=state))

@router.get('/mybookings', response_model_by_alias= List[models.showBookingDetails], status_code=status.HTTP_200_OK)
def list_all_booking_user(user_info: models.User = Depends(auth.get_current_user_role_and_id)):
    ''' List all booking of an user
    Arguments:
        None
    Returns:
        List of bookings
    '''
    data = []
    user_role, user_id = user_info.role, user_info.user_id
    try:
        data = database.fetch_data("orders",{"user_id": ObjectId(user_id)})
    except Exception as e:
        print(e)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "No bookings found!")
    for each_booking in data:
        each_booking = objectid_to_string(each_booking)
    data = [models.showBookingDetails(**x) for x in data ]
    res = [x.__dict__ for x in data]
    return res

@router.post('/{city}/{state}/{book_date}/{seats_qty}', response_model_by_alias=models.showBookingDetails, status_code=status.HTTP_201_CREATED)
def book_ticket(city: str, book_date: str, seats_qty: int, state:str, user_info: models.User = Depends(auth.get_current_user_role_and_id)):
    ''' Book ticket for a given date
    Arguments:
        request : models.Cities
    Returns:
        booking_details: models.showBookingDetails
    '''
    user_role, user_id = user_info.role, user_info.user_id
    city_name = city
    book_date_obj = datetime.strptime(book_date, "%Y-%m-%d")
    if datetime.today().date()>book_date_obj.date():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Booking date!")
    city_id = database.get_city_id(city.lower(), state)
    bus_id = database.get_bus_id(city_id)
    if not bus_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Bus found!")
    bus_seats_booked = 0
    aggregate_query = aggergations.get_available_seats(bus_id, book_date_obj)
    try:
        data = database.aggregation("orders", aggregate_query)[0]
        bus_seats_booked = data.get("count")
    except Exception as e:
        print(e)
    total_seats_in_bus = database.fetch_data("bus_info", {"_id": ObjectId(bus_id)})[0].get("total_seats")
    seats_available = total_seats_in_bus - bus_seats_booked
    if not seats_available:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No Seats Available")
    if seats_available < seats_qty:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please select fewer seats!")
    new_order = {
        "user_id": ObjectId(user_id),
        "bus_id": ObjectId(bus_id),
        "city_id": ObjectId(city_id),
        "date_of_booking": datetime.utcnow(),
        "date_of_departure": book_date_obj,
        "Number_of_seats_booked": seats_qty,
        "city_name": city_name
    }
    booking_id = database.add_data("orders", new_order)
    booking_details = database.fetch_data("orders", {"_id": ObjectId(booking_id)})[0]
    booking_details = objectid_to_string(booking_details)
    data = models.showBookingDetails(**booking_details).__dict__
    return data

@router.patch('/cancel/{booking_id}/{seats_qty}', status_code=status.HTTP_204_NO_CONTENT)
def cancel_ticket(booking_id: str, seats_qty: int, user_info: models.User = Depends(auth.get_current_user_role_and_id)):
    ''' Book ticket for a given date
    Arguments:
        request : models.Cities
    Returns:
        None
    '''
    fetch_booking_details = database.fetch_data("orders",{"_id": ObjectId(booking_id)})[0]
    if not fetch_booking_details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not booking found!")
    seats_booked = fetch_booking_details.get("Number_of_seats_booked")
    if seats_qty > seats_booked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booked seats is less than the seats given to cancel!")
    tickets_left = seats_booked - seats_qty
    if not tickets_left:
        database.delete_record("orders", {"_id": ObjectId(booking_id)})
    else:
        database.update_record("orders", {"_id": ObjectId(booking_id)}, {"Number_of_seats_booked": tickets_left})
    return {"message": "successful"}