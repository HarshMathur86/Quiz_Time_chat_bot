from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode, StickerFormat
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from config import properties_loader as properties
from mongodb import mongo_utils as mongodb
from rediscache import redis_utils as rediscache
from utils import sticker_utils as sticker
from utils.logger import log
from pyinstrument import Profiler


async def get_sticker_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.sticker:
        sticker_id = update.message.sticker.file_id
        print(f"Sticker ID: {sticker_id}")
        await update.message.reply_text(f"Latest Sticker ID: {sticker_id}")

# Application.createTask https://docs.python-telegram-bot.org/en/v20.0a0/telegram.ext.application.html?highlight=create_task#telegram.ext.Application.create_task

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    pf = Profiler()
    pf.start()
    log.info("{} - start command initiated".format(update.message.chat_id))

    await sticker.send_sticker(update, properties.HI_STICKER, "HI_STICKER")
    await update.message.reply_text(
        "Hi <b>{}!</b>".format(str(update.message.from_user.full_name)),
        parse_mode=ParseMode.HTML
    )
    context.application.create_task(mongodb.update_chat_id(update.message.chat_id))
    context.application.create_task(rediscache.update_chat_context(str(update.message.chat_id), "cmd_start"))

    keyboard = [[InlineKeyboardButton("CLICK ME", callback_data=0)]]
    await update.message.reply_text(
        "<b>I am here to help you improve your proficiency through stunning quizzes.</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
    )

    pf.stop()
    log.info(" time taken entire start command - {}".format(pf.last_session.duration))




def main() -> None:
    """Run bot."""

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(properties.BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Sticker.ALL, get_sticker_id))


    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)



if __name__ == "__main__":
    main()