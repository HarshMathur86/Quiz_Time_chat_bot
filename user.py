
from telegram import InlineKeyboardButton, Poll, ParseMode
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram import Bot

from database import execute_query

from urllib.request import urlopen
from urllib.parse import unquote
import json
import random

import time
import threading
import schedule

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from io import BytesIO
import cv2

import logging


# Enabling Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


bot = Bot(token="SAMLE")

message = {
    "kh" : "<b>Are you <i>Knowledge Hungry</i></b>, What do you think?\nWhy not test your intellect with some brain teasing challenges💪🧠",
    "mm" : " 🧐 Explore the sevices:",
    "pnr": "Looks like you haven't set your name for the <i><b>multiplayer quiz competition</b></i>.\nPlease send your name which will be visible to other players.",
    "mqc": "Welcome <b>{}</b>, \nI can also conduct multiplayer quizzes. Here you can check your position among your peers.\n\n 📌 <b>Rules for multiplayer quiz competition:</b>\n\n👉 Multiplayer quiz competition will last 7 minutes and contain 15 questions.\n👉 Questions will be asked in any field.\n👉 There will overall timer for the competition and no individual timer will be there.\n👉 Your leaderboard score will be calculated by keeping the time taken to answer the questions into consideration.\n👉 You can skip any question if you want to.\n\n<b>Are you ready for the challenge?</b>",
    "qe" : "😁 Wanna try some more things?",
    "ir" : "Please, accept my sincere apology for any technical problem. <b>Just write it out.</b>",
    "help": "👋  Hello, Quiz Time is a chat bot able to conduct some amazing quizzes in single player as well as multiplayer mode.\n\n👉 The bot with the help of quizzes can promote deeper engagement and help in the development of important learning skills.\n\n👉 It's guidance and performance reports will help you to improve your performance.\n\n👉 It's appealing interface with great interactivity which will encourage the user to participate in quizzes.\n\nYou can also use different commands like:\n\n/start - <i>Start the bot</i>\n/services - <i>Services provided by bot</i>\n/help - <i>Usage guide of Bot</i>\n/solo_quiz - <i>Single player Quiz</i>\n/multiplyer_quiz - <i>Multiplayer Quiz</i>"
}

topics = {
    18: "Computer",
    21: "Sports",
    10: "Books",
    22: "Geography",
    23: "History",
    27: "Animals",
    24: "Politics",
    17: "Science & Nature",
    9: "General Knowledge",
    0: "Any Category"
}

# Used in graph generation of player progess report
bar_colors_topic_wise = {
    18: "darkgreen",
    21: "slategrey",
    10: "yellow",
    22: "navy",
    23: "hotpink",
    27: "orange",
    24: "red",
    17: "pink",
    9: "aqua",
    0: "saddlebrown"
}


inline_keyboards = {
    "mm" : [
        [
            InlineKeyboardButton("Solo Quiz", callback_data=1) # Quick quiz - 'qq'
        ],
        [
            InlineKeyboardButton("Practice Arena", callback_data=2) # Customized quiz - 'cq'
        ],
        [
            InlineKeyboardButton("Multiplayer Quiz Competition", callback_data=3) # 'mqc'
        ],
        [
            InlineKeyboardButton("Progress Analysis", callback_data=4)
        ],
        [
            InlineKeyboardButton("Multiplayer Quiz Ranking", callback_data=5)
        ],
        [
            InlineKeyboardButton("Report any issue", callback_data=6)
        ]
    ],

    # Callback data of following keyboard button are topic codes for API call
    # Topic
    "cq-1" : [
        [
            InlineKeyboardButton("Computer", callback_data=18),
            InlineKeyboardButton("Sports", callback_data=21)
        ],
        [
            InlineKeyboardButton("Books", callback_data=10),
            InlineKeyboardButton("Geography", callback_data=22)
        ],
        [
            InlineKeyboardButton("History", callback_data=23),
            InlineKeyboardButton("Animals", callback_data=27)#15
        ],
        [
            InlineKeyboardButton("Politics", callback_data=24),#15
            InlineKeyboardButton("Science & Nature", callback_data=17)
        ],
        [
            InlineKeyboardButton("General Knowledge", callback_data=9),
            InlineKeyboardButton("ANY CATEGORY", callback_data="None")
        ],
        [
            InlineKeyboardButton("Terminate Quiz Session", callback_data=0)
        ]
    ],

    # Number of questions
    "cq-2":[
        [
            InlineKeyboardButton("5", callback_data=5),
            InlineKeyboardButton("10", callback_data=10),
            InlineKeyboardButton("15", callback_data=15)
        ]
    ],

    # Difficulty level
    "cq-3":[
        [
            InlineKeyboardButton("🟩 Easy", callback_data="easy"),
            InlineKeyboardButton("🟧 Medium", callback_data="medium"),
            InlineKeyboardButton("🟥 Hard", callback_data="hard")
        ],
        [
            InlineKeyboardButton("Any Difficulty", callback_data="None")
        ]
    ],

    # Time limit in seconds
    "cq-4":[
        [
            InlineKeyboardButton("15", callback_data=15),
            InlineKeyboardButton("30", callback_data=30),
            InlineKeyboardButton("45", callback_data=45),
            InlineKeyboardButton("60", callback_data=60)
        ],
        [
            InlineKeyboardButton("Unlimited Time", callback_data="None")
        ]
    ],

    # Starting multiplayer quiz battle
    'mqc':[
        [
            InlineKeyboardButton("Start multiplayer quiz", callback_data=1)
        ],
        [
            InlineKeyboardButton("🔙 to main menu", callback_data=0)
        ]
    ],

    'qe':[
        [
            InlineKeyboardButton("🔙 to main menu", callback_data=0)
        ]
    ]

}

# previous_message_sent keeps the record of the last sent message for futher processing of the responses
previous_message_sent = {}

####### Single player object containing variables ##########
parameters = {}
single_player_quiz_objects = {}

####### Multiplayer object keeping variables ###############
opened_window_multiplayer_object = None # Multiplayer object whoose joining window is open
ongoing_multiplayer_quiz_objects = {}   # {multiplayer_quiz_id : Ongoing multiplayer quiz objects }
previous_question_message_id = {}

#################### MULTI THREADING - Creating seprate thread for scheduling function ###################

#dummy scheduled function()
def dummy_fun():
    return
schedule.every(24).hours.do(dummy_fun)

def scheduled_functions_handler():
    while len(schedule.get_jobs())>0:
        #print("Running from global - ", threading.current_thread(), " - ", len(schedule.get_jobs()))
        
        time.sleep(1)
        #print("Inside loop - window_closer_scheduler id = {} = ".format(self.multiplayer_quiz_id), threading.current_thread())
        try:
            schedule.run_pending()
        except Exception as E:
            print("\n\n Inside the except of run_pending - ", E)

    # Killing the thread intentionally
    try: 
        raise BaseException("\n\nKilling the window cloasing thread")
    except:
        print("\nthis is the except block of window sending thread - ", threading.current_thread(), "\n")
        pass 

scheduler_thread = threading.Thread(target=scheduled_functions_handler)
scheduler_thread.setName("SchedulerThread")
scheduler_thread.start()
logger.info("Scheduler Thread Initiated")


################### PLAYER CLASS #############################

class Player:
    """Player class will keep all the player relevant data and 
        processing methods instead directly saving this on the 
        Quiz class and its Child classes """
    

    def __init__(self, chat_id, not_answered_ques):
        self.chat_id = chat_id
        self.total_questions = None
        self.not_answered_ques = not_answered_ques
        self.correct_answers = 0
        self.time_per_que = None
        self.stop_time = None
        self.que_idx = 0
        self.is_result_generated = False
        self.flag = None

    def pie_chart_generator(self):
        ######## Saving raw pie chart in Buffer ####################

        # Sizes = [Incorrect Percentage, Correct Percentage]
        correct = (self.correct_answers/self.total_questions) * 100
        sizes = [100-correct, correct]

        self.flag = 0
        
        def filler(sizes):
            """Used to label wedges of pie chart with their numeric value via a lambda function"""
            print("\nFILLER")
            print("correct = ", correct)
            print("correct = ", correct)
            print("correct - int(correct)  ---> ", correct - int(correct))
            if correct.is_integer():
                if self.flag == 0:
                    self.flag += 1
                    return "{:d}%\n Incorrect".format(int(sizes[0]))
                else:
                    return "{:d}%\n Correct".format(int(sizes[1]))
            else:
                if self.flag == 0:
                    self.flag += 1
                    return "{:.2f}%\n Incorrect".format(sizes[0])
                else:
                    return "{:.2f}%\n Correct".format(sizes[1])


        # Generating pie chart image
        plt.figure(figsize=(512/150,512/150), dpi=150)
        plt.pie(sizes, colors=['red', 'forestgreen'], autopct=lambda pct: filler(sizes), startangle=90, 
                wedgeprops = {'linewidth': 15}, 
                textprops = {'fontsize': 15, 'fontfamily': 'sans-serif', 'weight': 'bold'})
    
        plt.title('Result', fontdict={'fontsize':25, 'fontfamily': 'sans-serif', 'weight': 'bold'})
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Saving 'RGB' image into IO Buffer
        bio = BytesIO()
        bio.name = "pie_chart"
        plt.savefig(bio, transparent=True, dpi=150)

        ##### Converting the 'RGB' image into 'RGBA' format & then removing background ############
        #bio.seek(0)

        #image = Image.open(bio)
        #image.convert('RGBA')
        
        #bio.flush()
        #bio.close()

        #data = image.getdata()
        #new_data = []
        
        # Removing white background of the pie chart image
        #for pixel_triplet in data:
        #    if pixel_triplet[0] == 255 and pixel_triplet[1] == 255 and pixel_triplet[2] == 255: 
        #        new_data.append((255, 255, 255, 0))
        #    else:
        #        new_data.append(pixel_triplet)

        #image.putdata(new_data)

        # Saving new image again in IO Buffer
        #bio = BytesIO()
        #bio.name = "pie_chart"
        
        #image.save(bio, 'PNG')

        # Sending the sticker to the Player
        bio.seek(0)
        bot.send_sticker(self.chat_id, bio)
        bio.flush()
        bio.close()


    def result_generator(self, start_time, topic_id, is_single_player_result = True):
        print("\nINSIDE result generator - ", threading.current_thread())


        if self.is_result_generated:
            return schedule.CancelJob

        self.is_result_generated = True

        self.time_per_que = (time.time() - start_time) / self.que_idx # time per total attempted question
        
        if topic_id is None:
            topic_id = 0
        # Sending pie chart
        self.pie_chart_generator()

        # Sending message regarding the performance of user
        message = bot.send_message(
            self.chat_id, 
            "<b>Here is your performance in above quiz: </b>\n\n<i>Total questions attempted : </i><b> {:d}\n</b><i>Missed/skipped questions : </i><b> {:d}\n</b><i>Time per question (sec) : </i><b> {:.2f}\n</b>".format(self.total_questions, self.not_answered_ques, self.time_per_que), 
            parse_mode=ParseMode.HTML
        )


        # Updating the record on database
        if is_single_player_result:
            bot.editMessageReplyMarkup(self.chat_id, message.message_id, reply_markup = InlineKeyboardMarkup(inline_keyboards['qe']))

            execute_query("insert into SINGLE_PLAYER_QUIZ_RECORDS values({:d}, {:f}, {:f}, {:d}, CURRENT_timestamp);".format(self.chat_id, 
                                                                                    (self.correct_answers/self.total_questions) * 100,
                                                                                    self.time_per_que,
                                                                                    topic_id))
            global single_player_quiz_objects
            del single_player_quiz_objects[self.chat_id]
        else:
            bot.send_message(self.chat_id, "Generating leaderboard please wait.")
            # Logic of database updation
            global previous_message_sent
            del previous_question_message_id[self.chat_id]

        previous_message_sent[self.chat_id] = 'qe'
        return schedule.CancelJob

    # i=not useful
    def print_result(self):
        print("Result Details",self.total_questions, self.not_answered_ques, self.correct_answers, self.time_per_que, sep='\n')

###############################################################

################### QUIZ CONDUCTING CLASSES #############################

class Quiz:
    
    def __init__(self, parameters):
        # list with four parameters [topic(int), no of ques(int), difficulty(string/none), in sec per que]
        self.parameters = parameters
        # questions = {"question": [[correctanswer], [incorrect answers]] }
        self.questions = {}
        self.start_time = time.time()
    
    
    def generate_questions(self):
        #"https://opentdb.com/api.php?amount=10&category=23&difficulty=medium&encode=url3986"
        # Url formatting as per users choice
        
        url = "https://opentdb.com/api.php?amount=" + str(self.parameters[1])
        if self.parameters[0] is not None:
            url += "&category=" + str(self.parameters[0])
        if self.parameters[2] is not None:
            url += "&difficulty=" + str(self.parameters[2])
        url += "&encode=url3986"
        
        print(url)
        
        # Open Trivia Database API
        r = urlopen(url)
        data = r.read()
        data = json.loads(data)
        
        if data["response_code"] != 0:
            print("Insufiicient no of questions please use less no of questions")
            return
        data = data["results"]
        
        #print(data)
        for que_dict in data:
            options = [unquote(opt) for opt in que_dict.get('incorrect_answers')]
            correct_answer = unquote(que_dict.get('correct_answer'))
            options.append(correct_answer)
            random.shuffle(options)
            
            self.questions[unquote(que_dict.get('question'))] =[options, options.index(correct_answer)]
        
    
    def check_answer(self, que_idx, answered_idx):
        """ans_idx is the index of answered question by the user of bot"""
        que = list(self.questions.keys())[que_idx-1] # decremented by 1 because current que_idx is of next question.
        #print(que)
        #print(self.questions[que])
        #print(answered_idx)
        if self.questions[que][1] == answered_idx:
            print("correct")
            return True
        else:
            return False

    
    def send_question(self, player, context):
        pass

class SinglePlayer(Quiz):
    
    def __init__(self, parameters, chat_id):
        super().__init__(parameters)
        super().generate_questions()
        print("object created")

        self.player = Player(chat_id, self.parameters[1])
        self.timer_thread = None
        self.player.total_questions = self.parameters[1]
        #self.is_result_sent = False

   
    def send_question(self, context, next_que_idx=None):
        if next_que_idx is not None:
            
            if next_que_idx < self.player.que_idx:
                print("IF - Next question index", next_que_idx, threading.current_thread())
                print("NEXT QUE IDX - ", next_que_idx)
                return schedule.CancelJob

            if next_que_idx == self.parameters[1] and self.player.is_result_generated is False:
                self.player.result_generator(self.start_time, self.parameters[0])

                return  schedule.CancelJob

        que = list(self.questions.keys())[self.player.que_idx]

        if self.parameters[3] is None:
            # Unlimited time limit question
            message = bot.send_poll(
                self.player.chat_id, 
                question = "({}) ".format(self.player.que_idx + 1) + que, 
                options = self.questions[que][0], 
                is_anonymous = True, 
                type = Poll.QUIZ, 
                correct_option_id = self.questions[que][1]
            )
            
            print("\ncalled from(" +  str(self.player.que_idx+1)+ ") - ", threading.current_thread(), "\n")
        
        else:
            # Limited time limt question ( With Timer)
            message = bot.send_poll(
                self.player.chat_id, 
                question = "({}) ".format(self.player.que_idx + 1) + que, 
                options = self.questions[que][0], 
                is_anonymous = True, 
                type = Poll.QUIZ, 
                correct_option_id = self.questions[que][1],
                open_period = self.parameters[3]
            )

            self.timer_scheduler(context, self.player.que_idx + 1)
            #print("\ncalled from(" +  str(self.player.que_idx+1)+ ") - ", threading.current_thread(), "\n")
            
            
        payload = {
        message.poll.id: {"chat_id": self.player.chat_id, "message_id": message.message_id}
        }
        context.bot_data.update(payload)

        self.player.que_idx += 1
        print("INDEX INCREMENTED")
        
        return schedule.CancelJob


    def recieved_answer_processor(self, answered_idx, context):

        # Reducing not_answered_ques by 1 b/c initially not_answered_ques stores total no of questions
        self.player.not_answered_ques -= 1
        print("Inside recieved answer processor - ", self.player.not_answered_ques)
        
        try:
            if super().check_answer(self.player.que_idx, answered_idx):
                self.player.correct_answers += 1

            self.send_question(context)
        
        except IndexError: # Index of list out of range when all questions are sent
            # Implementing RESULT GENERATION 
            print("\n\n - Intitating result generation process - ", IndexError.__class__,  "\n\n")
            
            #self.is_result_sent = True
            self.player.result_generator(self.start_time, self.parameters[0])
        
        except Exception as exp:
            print("New exception ocuured - ", exp, ", with class - ", exp.__class__)

    def timer_scheduler(self, context, next_que_idx):
        if next_que_idx == self.parameters[1]:
            # Scheduling result generator instead of send question for last question
            schedule.every(self.parameters[3]).seconds.do(self.player.result_generator, self.start_time, self.parameters[0])
        else:
            schedule.every(self.parameters[3]).seconds.do(self.send_question, context, next_que_idx)


##########################################################################################
class Multiplayer(Quiz):
    def __init__(self):
        super().__init__([9, 15, None])
        super().generate_questions()
        print("Mulptiplayer object created")

        self.multiplayer_quiz_id = None
        # self.players = {chat_id : obj of Players class}
        self.players = {}
        self.players_score = []
        self.is_window_open = True
        self.players_quiz_completed_count = 0
        self.window_thread = None
        self.competition_thread = None
        self.start_time = None
        self.is_leaderboard_generated = False
        
        # Flags for countering multi calling due to multiple threads
        self.is_window_closed = False
        self.is_quiz_compeleted = False

        self.id_generator()

        self.skip_button = [[InlineKeyboardButton("SKIP QUESTION", callback_data="{}-{}".format(self.multiplayer_quiz_id, 2))]]
        

    def id_generator(self):
        data = execute_query("select max(multiplayer_quiz_id) from MULTIPLAYER_QUIZ_RECORDS;")
        
        if len(data) == 0:
            self.multiplayer_quiz_id = 1
        else:
            global ongoing_multiplayer_quiz_objects
            self.multiplayer_quiz_id = int(data[0]["max"] + 1) + len(ongoing_multiplayer_quiz_objects.keys())
        
        print("ID generated successfully - ", self.multiplayer_quiz_id)

    def joining_request_reciever(self, chat_id, context):
        if chat_id in self.players.keys():
            # When user clicks start multplayer battle switch multiple time so just returning with any operation
            return
        
        self.players[chat_id] = Player(chat_id, 15)
        self.players[chat_id].total_questions = 15

        print(self.players)

        if len(self.players.keys()) == 20: # max 20 players in a multiplayer battle
            self.window_closer(context)

        # Sending success message and telling to wait b/c other players are still joining
        bot.send_message(chat_id, "Congrats, you are in 🙂. Please wait for some time let other users join.")
    
    def leaderboard_generator(self):

        self.is_leaderboard_generated = True

        print("\nInside leader board generator - ", threading.current_thread())
        
        # Rank wise sorting of players
        for chat_id, player in self.players.items():
            self.players_score.append((chat_id, player.correct_answers / player.time_per_que * 300))

        print("self.players_score = ", self.players_score)
        
        self.players_score = sorted(self.players_score, key=lambda x:x[1], reverse=True)

        print(self.players_score)
        # Name extraction from database of top 3 players
        top_players_name = []
        
        for chat_id, _ in self.players_score[:3]:
            data = execute_query("select player_name from MULTIPLAYER_QUIZ_PARTICIPANTS_NAME where chat_id={};".format(chat_id))
            top_players_name.append(data[0]["player_name"])

        #Entering Dummy data
        
        #top_players_name.append("Player 3")
        print(top_players_name)

        print("# Editing the podium image")

        bgr = cv2.imread("Resources/podium.jpg")
        rgb = cv2.cvtColor(bgr, cv2.COLOR_RGB2BGR)

        # FIRST Player name editing
        font_style = cv2.FONT_HERSHEY_TRIPLEX
        text_size = cv2.getTextSize(top_players_name[0], font_style, 2, 3)[0]
        X = int((rgb.shape[0] - text_size[0])/2)
        image_arr = cv2.putText(rgb, top_players_name[0], (X, 180), font_style, 2, (0,0,0), 3, cv2.LINE_AA, False)
        print(X)
        
        # SECOND Player name editing
        text_size = cv2.getTextSize(top_players_name[1], font_style, 2, 3)[0]
        X = int(4/5 * rgb.shape[0] - 1/2 * text_size[0])
        image_arr = cv2.putText(rgb, top_players_name[1], (X, 285), font_style, 2, (0,0,0), 3, cv2.LINE_AA, False)
        print(X)

        # Third Player name editing ---> Need to edit it
        text_size = cv2.getTextSize(top_players_name[2], font_style, 2, 3)[0]
        X = int(1/5 * rgb.shape[0] - 1/2 * text_size[0])
        image_arr = cv2.putText(rgb, top_players_name[2], (X, 335), font_style, 2, (0,0,0), 3, cv2.LINE_AA, False)
        print(X)

        #buffer write
        image = Image.fromarray(image_arr)
        from io import BytesIO
        bio = BytesIO()
        bio.name = 'edited_podium_buffer.jpeg'
        print("image.mode = ", image.mode)

        # If image is other than RGB than converting it to RGB format
        if image.mode != 'RGB':
            print("Converting to RGB")
            image = image.convert('RGB')

        # Generating ranklist to participants of multiplayer quiz bot
        rank_list = "<b>Leaderboard of above quiz</b>\n\nFollowing list contain players score:\n\n"
        rank = 1
        
        medals = {
            1: "🥇",
            2: "🥈",
            3: "🥉"
        }
        rank_alloter = lambda rank:"(" + str(rank) + ")" if rank > 3 else medals[rank]

        for chat_id, score in self.players_score: 
            data = execute_query("select player_name from MULTIPLAYER_QUIZ_PARTICIPANTS_NAME where chat_id={};".format(chat_id))
            rank_list += "<b>{} <i>{}</i> - {:.2f}</b>\n".format(rank_alloter(rank), data[0]["player_name"], score)
            rank += 1
        
        # Sending the image and leaderboard to all participants of the bot
        for chat_id, _ in self.players_score:
            image.save(bio, 'PNG')
            bio.seek(0)
            bot.send_photo(chat_id, photo=bio)
            print("Image sent successfully - ", chat_id)
            
            if previous_message_sent[chat_id] == 'qe':
                bot.send_message(chat_id, rank_list, reply_markup = InlineKeyboardMarkup(inline_keyboards['qe']) ,parse_mode=ParseMode.HTML)
            else:
                bot.send_message(chat_id, rank_list, parse_mode=ParseMode.HTML)


    def multiplayer_quiz_closer(self):
        """Quiz closing function"""
        if self.is_quiz_compeleted or len(self.players.keys()) < 3:
            print("Leaderboard generator called id = {}- ".format(self.multiplayer_quiz_id), threading.current_thread())
            return schedule.CancelJob

        self.is_quiz_compeleted = True
        print("Initiating multiplayer quiz closer")

        for chat_id in self.players.keys():
            
            if self.players[chat_id].is_result_generated is False:
                
                with open("Resources/Stickers/clock_showing_crab.tgs", "rb") as sticker:
                    bot.send_sticker(chat_id, sticker)
                
                bot.send_message(chat_id, "<b>TIMES UP</b>", parse_mode=ParseMode.HTML)
                self.players[chat_id].result_generator(self.start_time, 0, is_single_player_result = False)

        if self.is_leaderboard_generated is False:
            # Generating leaderboard podium image and the rank list
            self.leaderboard_generator()
            
        # Updating database
        execute_query("insert into MULTIPLAYER_QUIZ_RECORDS values({:d}, {:d}, current_timestamp);".format(self.multiplayer_quiz_id, len(self.players.keys())))
        print("Multiplayer record data updated successfully")
        
        try:
            for chat_id, score in self.players_score:
                execute_query("insert into MULTIPLAYER_QUIZ_PLAYERS_PERFORMANCE values ({}, {:d}, {:.2f}, {:.2f}, {:d});".format(
                                                    chat_id,
                                                    self.multiplayer_quiz_id,
                                                    score,
                                                    self.players[chat_id].time_per_que,
                                                    self.players_score.index((chat_id, score)) + 1      
                ))
        except Exception as E:
            print("Inside player records updation in database - ", E)


        # Deletion of multiplayer object 
        global ongoing_multiplayer_quiz_objects
        del ongoing_multiplayer_quiz_objects[self.multiplayer_quiz_id]

        return schedule.CancelJob

    def remaining_time_alter(self):
        if self.is_quiz_compeleted or len(self.players.keys()) < 3:
            print("remaining time alert called id = {}- ".format(self.multiplayer_quiz_id), threading.current_thread())
            return schedule.CancelJob

        print("Remaining from id = {}- ".format(self.multiplayer_quiz_id), threading.current_thread())
        for chat_id in self.players.keys():
            if self.players[chat_id].is_result_generated is False:
                bot.send_message(chat_id, "<b>Last 1 minute remaining</b>", parse_mode = ParseMode.HTML)

        return schedule.CancelJob


    def send_question(self, chat_id, context):
        if self.is_quiz_compeleted:
            return
        try:
            question = list(self.questions.keys())[self.players[chat_id].que_idx]
        except Exception as E:
            print("Last question skipped - ", E)
            # Generating result
            self.players[chat_id].result_generator(self.start_time, 0, is_single_player_result = False)
            self.players_quiz_completed_count += 1

            # Cheking if all the user has compeleted the quiz for closing the quiz
            
            if self.players_quiz_completed_count == len(self.players.keys()):
                print("All users compeleted the quiz - Generating the leaderboard.")
                #logic of leaderboard sending 
                if self.is_quiz_compeleted is False:
                    self.multiplayer_quiz_closer()

            return 

 
        message = bot.send_poll(
                chat_id, 
                question = "({}) ".format(self.players[chat_id].que_idx + 1) + question, 
                options = self.questions[question][0], 
                is_anonymous = True, 
                type = Poll.QUIZ, 
                correct_option_id = self.questions[question][1],
                reply_markup = InlineKeyboardMarkup(self.skip_button)
            )

        payload = {
        message.poll.id: {"chat_id": chat_id, "message_id": message.message_id, "multiplayer_quiz_id": self.multiplayer_quiz_id}
        }
        context.bot_data.update(payload)

        # Setting message for checking whether the answer recieved by the user is of recently asked question or not
        global previous_question_message_id
        previous_question_message_id[chat_id] = message.message_id
        print(previous_question_message_id)

        print("################### ongoing battle objects #################")
        print(ongoing_multiplayer_quiz_objects)
        self.players[chat_id].que_idx += 1
        print("Ques index  = ", self.players[chat_id].que_idx)


    def recieved_answer_processor(self, answered_idx, chat_id, context):
        self.players[chat_id].not_answered_ques -= 1
        print("Inside recieved answer processor of MULTIPLAYER QUIZ - ", self.players[chat_id].not_answered_ques)


        if super().check_answer(self.players[chat_id].que_idx, answered_idx):
            self.players[chat_id].correct_answers += 1      
        self.send_question(chat_id, context)


    def window_closer(self, context):
        if self.is_window_closed:
            print("Window closer called id = {}- ".format(self.multiplayer_quiz_id), threading.current_thread())
            return schedule.CancelJob

        global opened_window_multiplayer_object 
        
        # Constraint of minimum 3 players to start a multiplayer quiz battle
        
        if len(self.players.keys()) < 3:
            for chat_id in self.players.keys():
                bot.send_message(chat_id, "Sorry, Insuficient no of players.You can take single player quiz.\n<b>Click - /solo_quiz</b>", parse_mode = ParseMode.HTML)
                previous_message_sent[chat_id] = 'qe'
            opened_window_multiplayer_object = None
            return schedule.CancelJob

        self.is_window_closed = True
        print("Window closer, id = {} - ".format(self.multiplayer_quiz_id), threading.current_thread())
        self.is_window_open = False
        self.start_time = time.time()
        for chat_id in self.players.keys():
            self.send_question(chat_id, context)

        print("Quiz compeleted players count = ", self.players_quiz_completed_count)
        
        global ongoing_multiplayer_quiz_objects
        
        ongoing_multiplayer_quiz_objects[self.multiplayer_quiz_id] = opened_window_multiplayer_object
        opened_window_multiplayer_object = None
        return schedule.CancelJob

    def window_closer_scheduler(self, context):
        
        print("window_cloaser_scheduler id = {} - ".format(self.multiplayer_quiz_id), threading.current_thread())
        # Scheduling the functions

        # Window closer 
        schedule.every(7).seconds.do(self.window_closer, context)
        
        # reamining time alert when 2 minutes left
        schedule.every(7 + 6*60).seconds.do(self.remaining_time_alter)
        
        # Leaderboard generator
        schedule.every(7 + 6*60 + 60).seconds.do(self.multiplayer_quiz_closer)
        
        # Multiplayer objects deletion functions
        #print(schedule.get_jobs())

    def window_opener(self, chat_id, context):
        # Joining the first player of the multiplayer quiz competition 
        self.joining_request_reciever(chat_id, context)

        self.window_closer_scheduler(context)

     
###############################################################

############ Single Player quiz handling functions ##################

def parameters_accepter(chat_id, parameter):

    print("Inside parameters_acceptor with parameter = ", parameter)
    # if user want to terminate the quiz session(parameter = 0)
    if parameter == "0":
        # resend the "mm" label message
        print("0")
        print(type(parameter))
        bot.send_message(chat_id, get_message("mm"), reply_markup=InlineKeyboardMarkup(inline_keyboards['mm']))
        previous_message_sent[chat_id] = "mm"
        print(previous_message_sent)
        return None, None

    try:
        if parameter == "None":
            parameters[chat_id].append(None)
        elif parameter.isnumeric():
            parameters[chat_id].append(int(parameter))
        else:
            parameters[chat_id].append(parameter)
        print(parameters)
    
    except Exception as exp:
        # Just for security purpose exception will not arise
        print("New exception ocuured - ", exp, ", with class - ", exp.__class__)

    print("parameter accepter")
    if len(parameters[chat_id]) == 1:
        ###### Solo Quiz only takes one parameter of topic so rest will be given here  #########
        
        if previous_message_sent[chat_id] == 'qq':
            parameters[chat_id].append(10)   # 10 Questions
            parameters[chat_id].append(None) # any difficulty
            parameters[chat_id].append(60)   # 60 seconds per question
            
            ##### Summary of Solo Quiz(Quick Quiz)  #######
            if parameters[chat_id][0] is not None:
                return "<i><b>{}</b> category is selected.</i>".format(topics[parameters[chat_id][0]]), None
            else:
                return "<i>All category questions will be asked.</i>", None
        
        return "Select no of questions", InlineKeyboardMarkup(inline_keyboards['cq-2'])

    elif len(parameters[chat_id]) == 2:
        return "Select difficulty of questions", InlineKeyboardMarkup(inline_keyboards['cq-3'])

    elif len(parameters[chat_id]) == 3:
        return "How much time do you need per question(sec)? ⏰ ", InlineKeyboardMarkup(inline_keyboards['cq-4'])

    elif len(parameters[chat_id]) == 4:
        ##### Summary of Practice Arena(Custom Quiz)  #######
        if previous_message_sent[chat_id] == 'cq':
            return summary_generator(chat_id), None

def single_player_quiz_initiator(chat_id, context):
    ###### The "object creation" for QUICK/CUSTOM QUIZ  ########
        
    single_player_quiz_objects[chat_id] = SinglePlayer(parameters[chat_id], chat_id)
    single_player_quiz_objects[chat_id].send_question(context)

    del parameters[chat_id]

def summary_generator(chat_id):

    summary = "<b>Selected parameter of the quiz</b>\n\n<i>Topic : </i> "
    print("Parameters list\n")
    for ele in parameters[chat_id]:
        print(ele, " , type =  ", type(ele))
    if parameters[chat_id][0] is not None:
        summary += "<b>{}</b>\n".format(topics[parameters[chat_id][0]])
    else:
        summary += "<b>Any Category</b>\n"
    
    if parameters[chat_id][2] is not None:
        summary += "<i>Difficulty : </i> <b>{}</b>\n".format(parameters[chat_id][2].upper())
    else:
        summary += "<i>Difficulty : </i> <b>Any Difficulty</b>\n"

    summary += "<i>Number of questions : </i> <b>{}</b>".format(parameters[chat_id][1])
    
    if parameters[chat_id][3] is not None:
        summary += "\n<i>Time per question(sec) : </i> <b>{}</b>".format(parameters[chat_id][3])
    else:
        summary += "\n<i>Time per question : </i> <b>Unlimited</b>"

    return summary


############ Multiplayer Player quiz handling functions ##################

def set_player_name(chat_id, name):
    """Saves the users alias(Player name - Public) to the database and,
        send the option to start multiplayer battle with rules."""

    print("Inside - set player name")
    
    for letter in name:
        if letter.isalnum() or letter in ['@', '-', '_']:
            print("l - ", letter)
            continue
        else:
            bot.send_message(chat_id, "<b>Invalid Name</b>", parse_mode=ParseMode.HTML)
            bot.send_message(chat_id, "Please send valid name. Refer above 👆 instructions")
            return

    print("Adding name to database ")
    execute_query("insert into MULTIPLAYER_QUIZ_PARTICIPANTS_NAME values({:d}, \'{}\');".format(chat_id, name))
    bot.send_message(chat_id, "Name added successfully 😃")

    # Multiplayer quiz starting message
    bot.send_message(
                chat_id, get_message('mqc').format(name), 
                reply_markup = InlineKeyboardMarkup(inline_keyboards['mqc']), 
                parse_mode = ParseMode.HTML
            )

    previous_message_sent[chat_id] = 'mqc'
    print("updated successfully")

    # sending multiplayer quiz instruction

def multiplayer_quiz_initiator(chat_id, context):
    global opened_window_multiplayer_object
    print(opened_window_multiplayer_object)
    
    if opened_window_multiplayer_object is None:
        print("Creating new window")
        opened_window_multiplayer_object = Multiplayer()
        opened_window_multiplayer_object.window_opener(chat_id, context)
    else:
        print("Adding player to opened window")
        opened_window_multiplayer_object.joining_request_reciever(chat_id, context)



############ User Interation handling functions ###################

def get_message(label):
    return message[label]

def update_chat_id(chat_id):
    data = execute_query("select * from ARRIVED_USERS where chat_id={};".format(chat_id))
    if len(data) > 0:
        print("found")
        return
    data = execute_query("insert into ARRIVED_USERS values({});".format(chat_id))
    print(data)
    print("update chat id function")

########### Progress analysis generating funcions #################

def graph_generator(chat_id, marks, quiz_index, topic_wise_bar_colors):
    
    ########### Creating the graph - Bar plot #############
    print(threading.current_thread())
    plt.figure(figsize=(18, 12))
    plt.style.use("fivethirtyeight")

    # Bar graph of marks
    if len(quiz_index) >= 8:
        plt.bar(quiz_index, marks, tick_label=quiz_index, width=0.8, color=topic_wise_bar_colors)
    elif len(quiz_index) >=4:
        plt.bar(quiz_index, marks, tick_label=quiz_index, width=0.6, color=topic_wise_bar_colors)
    elif len(quiz_index) >=2:
        plt.bar(quiz_index, marks, tick_label=quiz_index, width=0.4, color=topic_wise_bar_colors)
    else: # when length will be 1
        plt.bar(quiz_index, marks, tick_label=quiz_index, width=0.2, color=topic_wise_bar_colors)

    # Horizontal line representing average marks
    plt.plot(quiz_index, [sum(marks)/len(quiz_index) for x in range(len(quiz_index))], label="Average = {:.2f}%".format(sum(marks)/len(quiz_index)), color = "black")

    plt.tick_params(axis='x', labelsize=20)
    plt.tick_params(axis='y', labelsize=20)
    
    plt.title("Graph containing marks of your last {} single-player quizzes\nBar colour corresponds to quiz topics".format(len(quiz_index)), fontsize=35)
    plt.xlabel("Quiz Sessions", fontsize=30)
    plt.ylabel("Marks Obtained (%)", fontsize=30)
    
    plt.ylim(0, 100)
    plt.xlim(quiz_index[0]-0.5, quiz_index[-1]+0.5)
    
    plt.legend(fontsize=25)
    
    for index, value in enumerate(marks):
        if value<=97:
            plt.text(int(quiz_index[0])+index, value+1, "{:.1f}".format(value),  fontsize=20, ha='center')
        elif value<=99:
            plt.text(int(quiz_index[0])+index, value-4, "{:.1f}".format(value),  fontsize=20, ha='center')
        else:
            plt.text(int(quiz_index[0])+index, value-4, "{:.1f}".format(value),  fontsize=19, ha='center')

    # Saving the plot image in buffer
    bio = BytesIO()
    bio.name = "marks_graph"
    plt.savefig(bio, dpi=50)
    #plt.savefig("marks graph.png", figsize=(2400/300, 3600/300), dpi=300)
    ###################################################################################################
    
    # Reading image from buffer and converting to numpy array
    graph = Image.open(bio)
    graph = np.array(graph.getdata()).reshape(graph.size[1], graph.size[0], 4)
    graph = graph[:, :, :3]

    bio.flush()
    bio.close()

    # Reading the color coded blocks image from Resouces and resizing it to attach to the graph
    blocks = cv2.imread("Resources/color_graph.jpg")
    blocks = cv2.cvtColor(blocks, cv2.COLOR_RGB2BGR)
    blocks = cv2.resize(blocks, (900, 510))

    # Combining the two images and convertin to float type and then make it a Image object
    combined_image = np.vstack([graph, blocks])
    combined_image = combined_image.astype(np.uint8)
    combined_image = Image.fromarray(combined_image) 

    # Saving the final Image to the Buffer memory
    bio = BytesIO()
    bio.name = "combined_image"
    combined_image.save(bio, 'PNG')

    # Sending the Image to the user
    bio.seek(0)
    bot.send_photo(chat_id, bio)
    bio.flush()
    bio.close()
    

def players_pa_generator(chat_id):
    """Generate the graph and report of player's perform """

    global bar_colors_topic_wise
    
    data = execute_query("select marks, time_per_que, topic from SINGLE_PLAYER_QUIZ_RECORDS where chat_id = {} order by timestamp;".format(chat_id))

    quiz_count = 0
    if len(data) >= 15:
        quiz_count = 15
    elif len(data) > 0:
        quiz_count = len(data)
        print("Less tham 15")
    else:
        # User has not taken part in single player quiz till now. So, returing
        bot.send_message(chat_id, "<b>Sorry, but haven't taken part in any single player quiz.</b>\nTo take quiz click - /solo_quiz", parse_mode=ParseMode.HTML)
        return

    bot.send_message(chat_id, "<b>Generating report please wait.</b>", parse_mode=ParseMode.HTML)

    marks = [float(row['marks']) for row in data[-quiz_count:]]
    topic_wise_bar_colors = [bar_colors_topic_wise[int(row['topic'])] for row in data[-quiz_count:]]
    quiz_index = [data.index(row)+1 for row in data[-quiz_count:]]

    
    print(topic_wise_bar_colors)
    print(marks)
    print(quiz_index)

    # Sending the graph to the user
    graph_generator(chat_id, marks, quiz_index, topic_wise_bar_colors)


    ############# Creating the message #############################################
    message = "<b>Here is your performance 📊 in the single player mode : </b>(Solo Quiz + Pratice Arena)\n\n"
    message += "<i>Total quiz attempted :</i> <b>{}</b>\n".format(len(data))
    
    del data

    # Overall average marks
    message += "<i>Overall average marks :</i> <b>{:.2f}%</b>\n".format(float(execute_query("select avg(marks) from SINGLE_PLAYER_QUIZ_RECORDS where chat_id={};".format(chat_id))[0]["avg"]))

    # Average time taken per second
    message += "<i>Average time taken per que :</i> <b>{:.2f} secs</b>\n\n".format(float(execute_query("select avg(time_per_que) from SINGLE_PLAYER_QUIZ_RECORDS where chat_id={};".format(chat_id))[0]["avg"]))

    # Best performance of of the user
    best_performance = execute_query("select marks, time_per_que, topic from SINGLE_PLAYER_QUIZ_RECORDS where chat_id={} and marks=(select max(marks) from SINGLE_PLAYER_QUIZ_RECORDS where chat_id={});".format(chat_id, chat_id))
    message += "<b>Best Performance(s):</b>\n    <i>Marks</i> <b>|</b> <i>Time per que</i> <b>|</b> <i>Topic</i>\n"
    
    for row in best_performance:
        message += "    <b>{:.2f}% <b>|</b> {:.2f} sec <b>|</b> {}</b>\n".format(
            float(row["marks"]), float(row["time_per_que"]), topics[int(row["topic"])]
        )


    # Worst performance of the user
    worst_performance = execute_query("select marks, time_per_que, topic from SINGLE_PLAYER_QUIZ_RECORDS where chat_id={} and marks=(select min(marks) from SINGLE_PLAYER_QUIZ_RECORDS where chat_id={});".format(chat_id, chat_id))
    message += "\n<b>Worst Performance(s):</b>\n    <i>Marks</i> <b>|</b> <i>Time per que</i> <b>|</b> <i>Topic</i>\n"
    
    for row in worst_performance:
        message += "    <b>{:.2f}% <b>|</b> {:.2f} sec <b>|</b> {}</b>\n".format(
            float(row["marks"]), float(row["time_per_que"]), topics[int(row["topic"])]
        )

    # Top 3 strogest topics average marks
    best_topics = execute_query("select avg(marks), topic from SINGLE_PLAYER_QUIZ_RECORDS where chat_id={} group by topic order by avg(marks) desc limit 3;".format(chat_id))
    message += "\n<b>Your strongest topics with average marks:</b>\n"
    
    for row in best_topics:
        message += " 📌 <i>{} :</i> <b>{:.2f}%</b>\n".format(
            topics[int(row["topic"])], float(row["avg"])
        )

    # Topic with most quizzes attempted by the user 
    message += "\n<i>Topic in which most quizzes were given by you :</i> "

    most_quizzed = execute_query("select count(topic), topic from SINGLE_PLAYER_QUIZ_RECORDS where chat_id={} group by topic order by count(topic) desc limit 1;".format(chat_id))

    for row in list(most_quizzed):
        if most_quizzed.index(row) == len(most_quizzed)-1:
            message += "<b>{}</b>".format(topics[int(row["topic"])])
        else:
            message += "<b>{}, </b>".format(topics[int(row["topic"])])

    
    # Sending the message to the user
    bot.send_message(chat_id, message, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(inline_keyboards["qe"]))
    previous_message_sent[chat_id] = "qe"

########### Multiplayer Leaderboard Generator #####################

def multiplayer_quiz_ranking_generator(chat_id):

    ############ First creating general message of multiplayer quiz ranking ##################
    data = execute_query("""
                    select mqpn.chat_id, mqpn.player_name, avg_table.avg_score from
                    (select chat_id, avg(score) as avg_score from MULTIPLAYER_QUIZ_PLAYERS_PERFORMANCE 
                    where score!=0
                    group by chat_id) as avg_table, 
                    MULTIPLAYER_QUIZ_PARTICIPANTS_NAME mqpn
                    where avg_table.chat_id=mqpn.chat_id 
                    order by avg_table.avg_score desc;
    """)

    ranking_message = "<i>Leaderboard of best performing players in multiplayer quiz</i>\n\n"
    
    medals = {
        1: "🥇",
        2: "🥈",
        3: "🥉"
    }
    rank_alloter = lambda rank:"(" + str(rank) + ")" if rank > 3 else medals[rank]

    current_player_rank = None
    current_player_score = None

    for index, row in enumerate(data):
        print(rank_alloter(index+1), row["player_name"], " - {:.2f}".format(row["avg_score"]))

        if current_player_rank is None:
            if int(row["chat_id"]) == chat_id:
                current_player_rank = index + 1
                current_player_score = float(row["avg_score"])
                if index+1 >10:
                    break
        
        if index+1 <= 10: 
            ranking_message += "<b>{} <i>{}</i> - {:.2f}</b>\n".format(rank_alloter(index+1), row["player_name"], row["avg_score"])
        elif current_player_rank is not None:
            break

    bot.send_message(chat_id, ranking_message, parse_mode=ParseMode.HTML)
    
    if current_player_rank is None:
        bot.send_message("Till now you haven't took part in multiplayer quiz, to take part click - /multiplayer_quiz")
        return
    

    ############ Creating user specific multiplayer performance report ########################
    user_performance_message = "<b>Your performance in multiplyer quiz competition(s):</b>\n\n"

    # Total multiplayer quizzesin which user participated 
    total_attempts = execute_query("select count(chat_id) from MULTIPLAYER_QUIZ_PLAYERS_PERFORMANCE where chat_id={};".format(chat_id))[0]["count"]
    user_performance_message += "<i>Total multiplayer quiz attempted </i>: <b>{}</b>\n".format(total_attempts)
    
    # Overall rank of the user in the leaderboard
    user_performance_message += "<i>Overall leaderboard rank </i>: <b>{}</b>\n".format(current_player_rank)
    
    # Overall average score of the user in the multiplayer quiz competition
    user_performance_message += "<i>Overall score </i>: <b>{:.2f}</b>\n".format(current_player_score)

    # higest score attain by user
    user_performance_message += "\n<i>Highest score </i>: <b>{:.2f}</b>\n".format(execute_query("select max(score) from MULTIPLAYER_QUIZ_PLAYERS_PERFORMANCE where chat_id={};".format(chat_id))[0]["max"])
    
    # Lowest score of the user
    if total_attempts > 1:
        user_performance_message += "<i>Lowest score </i>: <b>{:.2f}</b>\n".format(execute_query("select min(score) from MULTIPLAYER_QUIZ_PLAYERS_PERFORMANCE where chat_id={};".format(chat_id))[0]["min"])

    # User's best rank among all the multiplayer battle
    best_rank = execute_query("""
            select mqpp.leaderboard_rank, mqr.players_count from
            MULTIPLAYER_QUIZ_PLAYERS_PERFORMANCE mqpp,
            MULTIPLAYER_QUIZ_RECORDS mqr
            where mqr.multiplayer_quiz_id=mqpp.multiplayer_quiz_id and 
            mqpp.chat_id={} order by mqpp.leaderboard_rank, mqr.players_count desc limit 1;
        """.format(chat_id))

    user_performance_message += "\n<i>Best rank </i>: <b>{}</b> out of <b>{}</b> players\n".format(best_rank[0]["leaderboard_rank"], best_rank[0]["players_count"])


    # Sending the message back to user
    bot.send_message(chat_id, user_performance_message, reply_markup=InlineKeyboardMarkup(inline_keyboards["qe"]), parse_mode=ParseMode.HTML)

    previous_message_sent[chat_id] = "qe"


def main_menu_handler(chat_id, option):
    print("main_menu_handler")
    if option == 2:
        print("opt")
        previous_message_sent[chat_id] = 'cq'
        parameters[chat_id] = []
        bot.send_message(chat_id, "<i><b>WELCOME TO PRACTICE ARENA</b></i> \nselect your topic", reply_markup=InlineKeyboardMarkup(inline_keyboards["cq-1"]), parse_mode=ParseMode.HTML)

    elif option == 1:
        print("opt - 1")
        previous_message_sent[chat_id] = 'qq'
        parameters[chat_id] = []
        bot.send_message(chat_id, "<i><b>WELCOME TO SOLO QUIZ</b></i> \nSelect your topic", reply_markup=InlineKeyboardMarkup(inline_keyboards["cq-1"]), parse_mode=ParseMode.HTML)

    elif option == 3:
        print("Multiplayer online quiz")

        """ Checking whether name exist in multiplayer or not and if name 
        doesn't exist then it will send message to get player name
        whih will be written on the leaderboard to all players participatine in competition"""


        data = execute_query("select player_name from MULTIPLAYER_QUIZ_PARTICIPANTS_NAME where chat_id={};".format(chat_id)) 
        print("data = ", data)

        if len(data) == 0:
            previous_message_sent[chat_id] = 'pnr' # pnr = player name recieving
            bot.send_message(chat_id, get_message('pnr'), parse_mode=ParseMode.HTML)
            bot.send_message(chat_id, "<b>Name should be of maximum 9 characters without emoji & space.\nThough you can use these characters - @, -, _</b>", parse_mode=ParseMode.HTML)
            bot.send_message(chat_id, "📝")
        
        else:
            # Invitation of joining multiplayer quiz competition
            bot.send_message(
                                chat_id, get_message('mqc').format(data[0]["player_name"]), 
                                reply_markup=InlineKeyboardMarkup(inline_keyboards['mqc']), 
                                parse_mode=ParseMode.HTML
                            )
            
            previous_message_sent[chat_id] = 'mqc'
        
    elif option == 4:
        # Progress Analysis 
        players_pa_generator(chat_id)

    elif option == 5:
        # Multiplayer quiz leaderboard
        multiplayer_quiz_ranking_generator(chat_id)
        

    elif option == 6:# issue reporting
        with open("Resources/Stickers/text_please.tgs", "rb") as sticker:
            bot.send_sticker(chat_id, sticker)

        # Sending the instructions to the user to write the message which will be send to the admin via email
        bot.send_message(chat_id, get_message('ir'), parse_mode=ParseMode.HTML)

        previous_message_sent[chat_id] = 'ir'

