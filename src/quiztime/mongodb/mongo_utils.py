import logging
from pymongo import MongoClient
import os

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

DB_HOST = os.getenv("DB_HOST")
DB_CLIENT = os.getenv("DB_CLIENT")

# Connect to MongoDB
client = MongoClient(DB_HOST)
db = client[DB_CLIENT]
users_collection = db["users"]

async def is_chat_id_present(chat_id):
    return users_collection.find_one({"_id": chat_id}) is not None

async def update_chat_id(chat_id):
    try:
        if await is_chat_id_present(chat_id) is False:
            logging.info(f"{chat_id} - New user arrived")
            users_collection.insert_one({"_id": chat_id})
    except Exception as e:
        logging.error("Exception occurred while inserting chat ID", e)
