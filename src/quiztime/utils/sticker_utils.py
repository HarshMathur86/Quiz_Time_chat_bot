from telegram import Bot, Update
from telegram.error import *
import os
from .logger import log

async def send_sticker(update: Update, sticker_file_id, sticker_id):
    try:
        await update.message.reply_sticker(sticker_file_id)
        log.info(f"Sending sticker using sticker file id: {sticker_file_id}")
    except BadRequest:
         # Fail safe mechanism
         log.info(f"Using fail safe for send sticker with id: {sticker_id}")
         sticker_path = os.getenv("PATH_" + sticker_id)
         with open(sticker_path, "rb") as sticker:
             await update.message.reply_sticker(sticker)

