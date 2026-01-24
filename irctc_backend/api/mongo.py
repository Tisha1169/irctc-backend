from pymongo import MongoClient
from django.conf import settings

MONGO_URI = "mongodb://localhost:27017/"

client = MongoClient(MONGO_URI)

db = client["irctc_logs"]

booking_logs_collection = db["booking_logs"]
