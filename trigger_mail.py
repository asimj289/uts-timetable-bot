import os

from utils import send_smtp_mail

smtp_server = os.environ['GMAIL_SMTP_SERVER']
smtp_server_port = os.environ['GMAIL_SMTP_SERVER_PORT']
sender_email = os.environ['GMAIL_USERNAME']
sender_password = os.environ['GMAIL_PASSWORD']
recipient_email = os.environ['TIMETABLE_BOT_TO_EMAIL']

subject = 'Timetable bot email test'
message_body = 'This is a test to see if the email notifications are working.'

send_smtp_mail(smtp_server, smtp_server_port, sender_email, sender_password, recipient_email, subject, message_body)
