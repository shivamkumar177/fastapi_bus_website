from pymongo import MongoClient
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017")
db = client["bus_book"]

def get_db():
    return db

def fetch_data(collection, query):
    data = list(db[collection].find(query))
    return data

def aggregation(collection, query):
    data = list(db[collection].aggregate(query))
    return data

def get_city_id(city_name, city_state):
    return db["cities"].find_one({"name": city_name, "state": city_state}).get("_id")

def get_bus_id(city_id):
    return db["bus_info"].find_one({"city_id": ObjectId(city_id)}).get("_id")

def get_user(email):
    return db["users"].find_one({"email":email})

def add_data(collection, body):
    created_data = db[collection].insert_one(body)
    return created_data.inserted_id

def delete_record(collection, query):
    return db[collection].delete_many(query)

def update_record(collection, filter_query, values_to_update):
    return db[collection].update_one(
        filter_query,
        {"$set": values_to_update}
    )
