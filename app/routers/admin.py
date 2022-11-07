import json
from typing import List
from fastapi import APIRouter, status, HTTPException, Depends
import app.models as models
from app import database
from bson import ObjectId
from app import auth

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.get('/bookings/city', response_model_by_alias= List[models.BookingDetails], status_code=status.HTTP_200_OK)
def get_booking_details_for_city(city_id: str = None, city_name: str = None, user_info: models.User = Depends(auth.get_current_user_role_and_id)):
    ''' get booking details of a city
    Arguments:
        city_id
        city_name
    Returns:
        List of booking for a city
    '''
    user_role, user_id = user_info.role, user_info.user_id
    if user_role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not Authorized')
    args = locals()
    data = []
    try:
        filter_query = {}
        if city_id:
            city_id = ObjectId(city_id)
            filter_query["city_id"] = city_id
        if city_name:
            city_name = city_name.lower()
            filter_query["city_name"] = city_name
        data = database.fetch_data("orders",filter_query)
    except Exception as e:
        print(e, e.__traceback__.tb_lineno)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "No Bookings found for this city!")
    for each_booking in data:
        each_booking["_id"] = str(each_booking["_id"])
        each_booking["city_id"] = str(each_booking["city_id"])
        each_booking["user_id"] = str(each_booking["user_id"])
        each_booking["bus_id"] = str(each_booking["bus_id"])
    data = [models.Booking_details(**x) for x in data ]
    res = [x.__dict__ for x in data]
    return res

@router.get('/bookings/{booking_id}', response_model_by_alias= List[models.BookingDetails], status_code=status.HTTP_200_OK)
def get_booking_details_for_city(booking_id: str, user_info: models.User = Depends(auth.get_current_user_role_and_id)):
    ''' get booking details of a booking_id
    Arguments:
    Returns:
        Booking info of a booking_id
    '''
    user_role, user_id = user_info.role, user_info.user_id
    if user_role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not Authorized')
    args = locals()
    data = []
    try:
        filter_query = {"_id": ObjectId(booking_id)}
        data = database.fetch_data("orders",filter_query)
    except Exception as e:
        print(e, e.__traceback__.tb_lineno)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "No Bookings found for this booking_id!")
    for each_booking in data:
        each_booking["_id"] = str(each_booking["_id"])
        each_booking["city_id"] = str(each_booking["city_id"])
        each_booking["user_id"] = str(each_booking["user_id"])
        each_booking["bus_id"] = str(each_booking["bus_id"])
    res = [models.BookingDetails(**x) for x in data ]
    res = [x.__dict__ for x in res]
    return res

@router.post('/add_city', status_code=status.HTTP_201_CREATED)
def add_city(request: models.Cities, user_info: models.User = Depends(auth.get_current_user_role_and_id)):
    ''' add city
    Arguments:
        request : models.Cities
    Returns:
        None
    '''
    user_role, user_id = user_info.role, user_info.user_id
    if user_role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not Authorized')
    city_name = request.name
    city_state = request.state
    fetch_city = database.fetch_data('cities', {"name": city_name, "state": city_state})
    if len(fetch_city):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='{}, {} already exists'.format(city_name, city_state))
    # create city
    new_city_body = {
        "name": city_name,
        "state": city_state
    }
    created_city_id = database.add_data("cities", new_city_body)
    # create bus
    new_bus_body = {
        "total_seats": 40,
        "city_id": ObjectId(created_city_id)
    }
    created_bus_id = database.add_data("bus_info", new_bus_body)
    return {"message": "success"}

@router.delete('/delete/{city_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_city(city_id: str, user_info: models.User = Depends(auth.get_current_user_role_and_id)):
    ''' add city
    Arguments:
        request : models.Cities
    Returns:
        None
    '''
    user_role, user_id = user_info.role, user_info.user_id
    if user_role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not Authorized')
    fetch_city = database.fetch_data('cities', {"_id": ObjectId(city_id)})
    if not fetch_city:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='City not found!')
    # delete bus for that city
    database.delete_record("bus_info", {"city_id": ObjectId(city_id)})
    # delete bookings for that bus
    database.delete_record("orders", {"city_id": ObjectId(city_id)})
    # delete city
    database.delete_record("cities", {"_id": ObjectId(city_id)})
    return {"message": "success"}

