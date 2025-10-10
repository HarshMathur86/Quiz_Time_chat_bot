import asyncio
import logging
import os
from redis import Redis

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"
if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"


redis_client = Redis.from_url(
    REDIS_URL,
    decode_responses=True
)

async def update_chat_context(chat_id: str, context: str):
    try:
        expiry_seconds = 3 * 60 * 60
        await redis_client.setex(f"chat_context:{chat_id}", expiry_seconds, context)
        logging.info(f"Context updated for chat_id={chat_id}")
    except Exception as e:
        logging.error(f"Error occurred while updating context: {e}")

async def main():
    try:
        pong = await redis_client.ping()
        logging.info(f"Connected to Redis: {pong}")
        await update_chat_context("12345", "Hello from modern Redis client!")
    except Exception as e:
        logging.error(f"Redis operation failed: {e}")
    finally:
        await redis_client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
