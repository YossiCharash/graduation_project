from pymongo import MongoClient

mongo_client = MongoClient("mongodb://admin:1234@localhost:27017")
db = mongo_client["terrorism_data"]
collection = db["terrorism_attack"]

print("Connected to MongoDB!")