
import logging
from email_api import issue_alert_email_sender

from user import *
from admin import announcement, validate_admin

from telegram import  Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, PollHandler
from utlis import get_reply

# Enabling Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN = "SAMPLE"

# Defining a few command handlers. These usually take the two arguments update and context.

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    #sending hi sticker
    with open("Resources/Stickers/hand_hi.tgs", "rb") as sticker:
        update.message.reply_sticker(sticker)
    
    keyboard = [[InlineKeyboardButton("CLICK ME", callback_data=0)]]
    
    update.message.reply_text("Hi <b>{}!</b>".format(str(update.message.from_user.full_name)), parse_mode=ParseMode.HTML)
    update.message.reply_text("<b>I am here to help you improve your proficiency through stunning quizzes.</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
    
    update_chat_id(update.message.chat_id)

    logger.info("{} - start command initiated".format(update.message.chat_id))
    previous_message_sent[update.message.chat_id] = 's'


def multiplayer_competition(update: Update, _: CallbackContext):
    main_menu_handler(update.message.chat_id, 3)
    logger.info("{} - multiplayer_quiz command initiated".format(update.message.chat_id))


def single_player_quiz(update: Update, _:CallbackContext):
    main_menu_handler(update.message.chat_id, 1)
    logger.info("{} - solo_quiz command initiated".format(update.message.chat_id))


def help(update: Update, _:CallbackContext):
    update.message.reply_sticker("https://github.com/HarshMathur86/bot-resources/blob/main/quiz-time-logo.webp?raw=true")
    update.message.reply_text(get_message("help"), parse_mode=ParseMode.HTML)

    if validate_admin(update.message.chat_id):
        update.message.reply_text("<b>Welcome, Admin following command is for you</b>\n\n/announce - <i>for making an annoumcement to all the users of the bot</i>\n\nAlso, you can see the issues reported by the users in your registered email.", parse_mode=ParseMode.HTML)

    logger.info("{} - help command initiated".format(update.message.chat_id))


def services(update: Update, _:CallbackContext):
    update.message.reply_text(get_message("mm"), reply_markup=InlineKeyboardMarkup(inline_keyboards["mm"]))
    previous_message_sent[update.message.chat_id] = 'mm'

    logger.info("{} - services initiated".format(update.message.chat_id))


def text_message_handler(update: Update, _:CallbackContext):
    logger.info("{} - text message recieved".format(update.message.chat_id))
    chat_id = update.message.chat_id
    print(update.message.text)
    try:
        if previous_message_sent[chat_id] == 'pnr': # pnr - player's name recieving
            print("Validating player name")
            set_player_name(chat_id, update.message.text)
        
        elif previous_message_sent[chat_id] in ['qq', 'cq', 'mqc']:
            update.message.reply_text("🙏 Please do not interrupt quiz session.")
            
        elif previous_message_sent[chat_id] == 'ir':
            update.message.reply_text("Thanks for repoting issue it will be resolved shortly. Until then try out something else.\n<b>Click - /services</b>", parse_mode=ParseMode.HTML)
            issue_alert_email_sender(update.message.text, update.message.from_user.full_name)

        elif previous_message_sent[chat_id] == 'ann':
            announcement(update.message.text, chat_id)
            update.message.reply_text("<b>Announcement to all users is compeleted</b>", parse_mode=ParseMode.HTML)
            previous_message_sent[chat_id] = 's'
        
        else:
            raise BaseException("Text Communication")
    except:

        if "quiz" in update.message.text.lower():
            previous_message_sent[chat_id] = 'mm'
            update.message.reply_text(get_message("mm"), reply_markup=InlineKeyboardMarkup(inline_keyboards["mm"]))
            return

        print("Using google api")
        reply = get_reply(update.message.text, chat_id)
        print(reply)
        update.message.reply_text(reply)

    

    

def option_selector(update: Update, context: CallbackContext):
    query = update.callback_query
    
    recieved_query = query.data
    chat_id = query.message.chat_id
    query.message.reply_chat_action(ChatAction.TYPING)
    logger.info(str(chat_id) + " - callback query recieved - " + str(recieved_query))

    try:
        if previous_message_sent[chat_id] == "s":
            query.edit_message_reply_markup(reply_markup=None)
            # Do you know part
            with open("Resources/Stickers/thinking_fish.tgs", "rb") as sticker:
                query.message.reply_sticker(sticker)
            #query.message.reply_text(get_message("kh"), parse_mode=ParseMode.HTML)

            #time.sleep(1)
            #query.message.reply_text(get_message("mm"))
            query.message.reply_text(get_message("kh"), parse_mode=ParseMode.HTML)
            time.sleep(1)
            query.message.reply_text(get_message("mm"), reply_markup=InlineKeyboardMarkup(inline_keyboards['mm']), parse_mode=ParseMode.HTML)
            previous_message_sent[chat_id] = "mm" # main menu(mm)
            return

        elif previous_message_sent[chat_id] == "mm":
            query.edit_message_reply_markup(reply_markup = None)
            main_menu_handler(chat_id, int(recieved_query))
            return

        elif previous_message_sent[chat_id] == 'cq' or previous_message_sent[chat_id] == 'qq':
            print("inside cq/qq")

            if recieved_query == '0':
                query.edit_message_text("What else you want to do?", reply_markup=None)
            
            message, markup = parameters_accepter(chat_id, recieved_query)
            
            try:
                query.edit_message_text(message, parse_mode=ParseMode.HTML)
                query.edit_message_reply_markup(markup)
            except Exception as E:
                #print("EXP = ", E)
                #print("markp = ", markup)
                pass

            if len(parameters[chat_id]) == 4:
                with open("Resources/Stickers/hand_questionmark.tgs", "rb") as sticker:
                    query.message.reply_sticker(sticker)
                query.message.reply_text("Here comes your first question.")

                print("Initializing quiz")
                single_player_quiz_initiator(chat_id, context)

        elif previous_message_sent[chat_id] == 'mqc':
            
            if recieved_query == "1":
                try:
                    query.edit_message_reply_markup(reply_markup=None)
                except:
                    pass
                print("Initiating multiplayer quiz competition")

                #Starting multiplayer quiz
                multiplayer_quiz_initiator(chat_id, context)
            
            elif recieved_query == "0":
                query.edit_message_text("What else you want to do?")
                query.message.reply_text(get_message('mm'), reply_markup=InlineKeyboardMarkup(inline_keyboards['mm']))
                previous_message_sent[chat_id] = 'mm'
            
            elif recieved_query.endswith("-2"):
                query.edit_message_reply_markup(reply_markup=None)
                print(recieved_query[:-2])
                print(type(recieved_query[:-2]))
                print(recieved_query)
                ongoing_multiplayer_quiz_objects[int(recieved_query[:-2])].send_question(chat_id, context)
        
        elif previous_message_sent[chat_id] == 'qe' and recieved_query == "0":
            query.edit_message_reply_markup(reply_markup=None)
            query.message.reply_text(get_message('mm'), reply_markup=InlineKeyboardMarkup(inline_keyboards['mm']))
            previous_message_sent[chat_id] = 'mm'
    
    except:
        query.edit_message_reply_markup(reply_markup=None)
        query.message.reply_text("Please click - /services")
            

def poll_handler(update: Update, context = CallbackContext):

    answers = update.poll.options
    #update.callback_query.edit_message_reply_markup()
    answers = [answer['voter_count'] for answer in answers]
    ans_idx = answers.index(1)
    try:
        chat_id = context.bot_data[update.poll.id]["chat_id"]
        message_id = context.bot_data[update.poll.id]["message_id"]
    except KeyError:
        # when poll is answered after the quiz is ended (Only possible with question of unlimited time)
        return
    
    try:
        multiplayer_quiz_id = context.bot_data[update.poll.id]["multiplayer_quiz_id"]
    except KeyError:
        # when question answered is of single player battle
        pass

    logger.info("{} - quiz answer recieved".format(chat_id))
    
    # Single-Player quiz answer processing
    if previous_message_sent[chat_id] == 'cq' or previous_message_sent[chat_id] == 'qq':
        single_player_quiz_objects[chat_id].recieved_answer_processor(ans_idx, context)
    
    # Multiplayer quiz answer processing
    elif previous_message_sent[chat_id] == 'mqc' and previous_question_message_id[chat_id] == message_id:
        print("\n\nPoll recieved")
        print(answers)
        print(ans_idx)
        bot.editMessageReplyMarkup(chat_id, message_id = message_id, reply_markup = None)
        try:
            ongoing_multiplayer_quiz_objects[multiplayer_quiz_id].recieved_answer_processor(ans_idx, chat_id, context)
        except Exception as E:
            print("Poll reply markup editor - ", E)
        #ongoing_multiplayer_quiz_objects[multiplayer_quiz_id].recieved_answer_processor(ans_idx, chat_id, context)
    


def image_handler(update: Update, _:CallbackContext):
    logger.info("{} - announcement message recieved with image".format(update.message.chat_id))

    if validate_admin(update.message.chat_id):
        announcement(update.message.caption, update.message.chat_id, update.message.photo[-1])
        update.message.reply_text("<b>Announcement to all users is compeleted</b>", parse_mode=ParseMode.HTML)
        previous_message_sent[update.message.chat_id] = 's'
        

############### ADMIN Exclusie commands ################################
def announcement_initiator(update: Update, _: CallbackContext):

    # Checking whether admin is sending the message or not
    if validate_admin(update.message.chat_id):
        update.message.reply_text("Hello, admin please send the message you want anoounce 🗣 among <b>all users</b> of the bot.", parse_mode=ParseMode.HTML)
        previous_message_sent[update.message.chat_id] = 'ann' # announcement
        logger.info("{} - announce command initiated by admin".format(update.message.chat_id))
    else:
        pass


def main():

    updater = Updater(TOKEN)
    
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("multiplayer_quiz", multiplayer_competition))
    dispatcher.add_handler(CommandHandler("solo_quiz", single_player_quiz))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("services", services))

    ######### admin commands ################
    dispatcher.add_handler(CommandHandler("announce", announcement_initiator))    
    #########################################

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, text_message_handler))
    dispatcher.add_handler(MessageHandler(Filters.photo, image_handler))
    dispatcher.add_handler(CallbackQueryHandler(option_selector))
    dispatcher.add_handler(PollHandler(poll_handler))
    
    updater.start_polling()

    logger.info("Listening...\n\n")

    updater.idle()

if __name__ == '__main__':
    main()
