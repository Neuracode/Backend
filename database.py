from os import getenv
from  dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv()

MONGO_DB_URL = getenv('DATABASE_URL')

client = MongoClient(MONGO_DB_URL)

db = client.main
