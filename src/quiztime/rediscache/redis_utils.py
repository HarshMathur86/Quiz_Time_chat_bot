import logging
from redis.asyncio import Redis
import os

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

# Connect to Redis
# redis_client = rediscache.Redis(host='civil-silkworm-18913.upstash.io', password='AUnhAAIjcDEwMzk5MTcyOTI0OGY0NDYxOWJmYWI5M2NkNTQ0Nzk1OHAxMA', port=6379, ssl=True)
redis_client = Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        # password="sample123",
        decode_responses=True  # Ensures string responses instead of bytes
    )

async def update_chat_context(chat_id, context):
    try:
        # await redis_client.hset("chat_context", chat_id, context)
        await redis_client.setex(f"chat_context:{chat_id}", 3*60*60, context)  # Expiry: 6 hours
    except Exception as e:
        logging.error("Error occurred while updating context", e)

