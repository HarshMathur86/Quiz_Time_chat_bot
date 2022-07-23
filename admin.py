
from telegram import InlineKeyboardButton, ParseMode
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram import Bot

from database import execute_query

from user import inline_keyboards, previous_message_sent, get_message

import logging

# Enabling Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


bot = Bot(token="SAMPLE")


def admin_login():
    pass

######### Announcement ################
def announcement(message_to_announce, admin_chat_id, image=None):

    data = execute_query("select * from ARRIVED_USERS where chat_id!={};".format(admin_chat_id))

    if image is None:
        for row in data:
            try:
                bot.send_message(int(row["chat_id"]), message_to_announce)
                logger.info(str(row["chat_id"]) + " - annoucement sent")
            except:
                pass
    else:
        for row in data:
            try:
                bot.send_photo(int(row["chat_id"]), image, caption=message_to_announce)
                logger.info(str(row["chat_id"]) + " - annoucement sent")
            except Exception as e:
                pass
    
def validate_admin(chat_id):

    data = execute_query("select chat_id from ADMIN;")

    if chat_id == int(data[0]["chat_id"]):
        return True
    else:
        return False
