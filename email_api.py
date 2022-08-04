from mailjet_rest import Client
import logging 

from database import execute_query

# Enabling Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

def issue_alert_email_sender(message, username):
	message = message.replace("\n", "<br>")

	with open("Resources/alert_email.html", "r") as file:
		html_part = file.read()

	html_part = html_part.replace("[user_issue]", "{}".format(message))
	html_part = html_part.replace("[user_name]", "{}".format(username))

	admin_email = execute_query("select email from ADMIN;")[0]["email"]

	mailjet = Client(auth=('SAMPLE', 'SAMPLE'))

	data = {
		'FromEmail': 'SAMPLE@gmail.com', # Bot's email
		'FromName': 'Quiz Time Chatbot',
		'Subject': 'Quiz Time - Technical issue reported by {}'.format(username),
		'Text-part': 'Dear passenger, welcome to Mailjet! May the delivery force be with you!',
		'Html-part': html_part,
		'Recipients': [{'Email':'{}'.format(str(admin_email))}] #Admin's email
	}

	result = mailjet.send.create(data=data)
	
	if result.status_code == 200:
		logger.info("alert email successfully sent to admin")
		return True
	else:
		return False

