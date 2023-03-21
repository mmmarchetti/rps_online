from pymongo import MongoClient

client = MongoClient('mongo')
db = client["userInfo"]
users = db["users"]
rank = db["rank"] # rank in {"username", rank#} format
