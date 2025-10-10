# properties_loader.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

HI_STICKER = os.getenv("HI_STICKER")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not HI_STICKER:
    raise ValueError("HI_STICKER is not set in the environment or .env file")
else:
    print(f"Loaded HI_STICKER: {HI_STICKER}")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in the environment or .env file")
else:
    print(f"Loaded BOT_TOKEN")
