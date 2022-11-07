from bson import ObjectId
from datetime import datetime

def fetch_all_city_query():
    aggregate_query = [
        {
            '$lookup': {
                'from': 'bus_info', 
                'localField': '_id', 
                'foreignField': 'city_id', 
                'as': 'bus_info'
            }
        }, {
            '$project': {
                '_id': 0, 
                'name': 1, 
                'number_of_seats_available': '$bus_info.seats_remaining'
            }
        }, {
            '$unwind': {
                'path': '$number_of_seats_available'
            }
        }
    ]
    return aggregate_query

def get_available_seats(bus_id, date_of_departure):
    aggregate_query = [
        {
            '$match': {
                'bus_id': ObjectId(bus_id), 
                'date_of_departure': {
                    '$gte': date_of_departure
                }
            }
        }, {
            '$group': {
                '_id': None, 
                'count': {
                    '$sum': '$Number_of_seats_booked'
                }
            }
        }
    ]
    return aggregate_query