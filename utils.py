import requests
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def print_failed_response_details(failed_response):
    """
    Prints data about why a request failed.
    :param failed_response: the failed response
    :type failed_response: requests.Response
    :return:
    """
    print('---------------')
    print('REQUEST DETAILS')
    print('---------------')
    print('  REQUEST:')
    print('    Headers: %s' % (failed_response.request.headers,))
    print('    Body: %s' % (failed_response.request.body, ))
    print('')
    print('  RESPONSE:')
    print('    Headers: %s' % (failed_response.headers,))
    print('    Body: %s' % (failed_response.content,))
    print('')


def request_failed(failed_response, message=None, print_details=True):
    if print_details:
        print_failed_response_details(failed_response)
    raise requests.RequestException(message)


def has_env_variables():
    """
    Checks that the required environment variables have been set.
    :return:
    """
    required_env_variables = [
        'TIMETABLE_BOT_USERNAME',
        'TIMETABLE_BOT_PASSWORD',
        'TIMETABLE_BOT_SUBJECT',
        'TIMETABLE_BOT_CLASS_TYPE',
        'TIMETABLE_BOT_TO_EMAIL',
        'TIMETABLE_BOT_ACTIVITY_CODES', # Comma separated list of activity codes e.g. 03,05 (leading zeros required!)
        'GMAIL_USERNAME',
        'GMAIL_PASSWORD',
        'GMAIL_SMTP_SERVER',
        'GMAIL_SMTP_SERVER_PORT'
    ]

    environment_variables_fulfilled = True
    for env_variable in required_env_variables:
        if env_variable not in os.environ:
            print('%s environment variable must be set.' % (env_variable,))
            environment_variables_fulfilled = False

    return environment_variables_fulfilled


def send_smtp_mail(smtp_server, smtp_server_port, sender_email, sender_password, recipient_email, subject,
                   message_body):
    server = smtplib.SMTP(smtp_server, smtp_server_port)
    server.starttls()
    server.login(sender_email, sender_password)

    message = MIMEMultipart()

    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    message.attach(MIMEText(message_body, 'plain'))

    server.sendmail(sender_email, recipient_email, message.as_string())
    server.quit()


