from pymongo import MongoClient
from os import environ

PASSWORD = environ.get("MONGO_ROOT_PASSWORD", "password")

client = MongoClient(host="novara-mongo", port=27017, username="root", password=PASSWORD)
db = client.get_database("db")