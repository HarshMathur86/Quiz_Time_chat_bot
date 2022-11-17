# Quiz Time chat bot
 - Quiz time bot is a quiz conducting telegram based bot. Capable of conducting quizzes in single player as well as multiplayer modes and can also generate detailed progress report of the user.
 - The bot is implemented using ***python*** programming language and ***postgre SQL*** database.
 - Following APIs are used in the impelementation of the bot:
   - **Open Trivia Database API** - For generating questions of the quiz
   - **Dialogflow API (Google Cloud)** - For generating conversational responses of the bot.
   - **Mailjet API** - For sending emails to administrator of the bot.

 - The bot is deployed in ***Heroku Cloud***.

## Here are some snapshots of the bot

![alt text](https://github.com/HarshMathur86/bot-resources/blob/main/Quiz%20bot%20images/Image%201.png?raw=true)
![Image 6](https://user-images.githubusercontent.com/60878060/201970897-517b58e8-7d1b-48c0-8d29-174bae9c6100.png)

### Single Player Quiz
 - **Bot offers its users all kinds of customizations on the quizzes asked to them for better improvment of their knowledge.**

 ![](https://github.com/HarshMathur86/bot-resources/blob/main/Quiz%20bot%20images/Image%202.png)


 - **Single player quiz sessions generate result of the users and record user's performance. Which can later be used for generating detailed progess report of the user and, the image is generated in real time using python's image processing libraries like OpenCV & Pillow.**

<p align="center">
<img src="https://user-images.githubusercontent.com/60878060/201585132-b0ba2b08-6109-43d9-ace5-40d202b83f32.png" height="606" width="645"/>
<img src="https://user-images.githubusercontent.com/60878060/201585784-d9bb637a-5bd9-4166-8e4b-b555630a84a4.png"/>
</p>

 ### Multiplayer Quiz Session 
  - **Muliplayer quiz asks same quiestion to all the players and then generate the leaderboard of the quiz where user can see their performance as shown in following image.**
 
 ![Image 5](https://user-images.githubusercontent.com/60878060/202222530-7b66709d-e897-4809-bc66-0784e918974a.png)
 
 ### Admin
  - **The bot alaso has a admin who has two more provilages one is admin can make an announcment to all the players of the bot and other is all the technical issues reported by the users of the bot are directed to admin via email.**

![Image 7](https://user-images.githubusercontent.com/60878060/202370649-845b53d2-c6c2-4e89-883f-b01520b30218.png)






