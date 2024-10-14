from pymongo import MongoClient
from os import environ

PASSWORD = environ.get("MONGO_ROOT_PASSWORD", "password")

client = MongoClient(host="mongodb", port=27017, username="root", password=PASSWORD)
db = client.get_database("db")