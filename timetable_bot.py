import requests
import os
import sys
import time

from utils import request_failed, has_env_variables, send_smtp_mail

BASE_URL = 'https://mytimetable.uts.edu.au/aplus2017/'


def send_mail(subject, message_body):
    smtp_server = os.environ['GMAIL_SMTP_SERVER']
    smtp_server_port = os.environ['GMAIL_SMTP_SERVER_PORT']
    sender_email = os.environ['GMAIL_USERNAME']
    sender_password = os.environ['GMAIL_PASSWORD']
    recipient_email = os.environ['TIMETABLE_BOT_TO_EMAIL']

    send_smtp_mail(smtp_server, smtp_server_port, sender_email, sender_password, recipient_email, subject, message_body)


def register_subject(session, login_token, student_code, class_key):
    enrol_subject_url = BASE_URL + 'rest/student/changeActivity/'
    params = {'ss': login_token}

    class_key_split = class_key.split('|')

    subject_code = class_key_split[0]
    class_type = class_key_split[1]
    class_id = class_key_split[2]

    data = {
        'token': 'a',
        'student_code': student_code,
        'subject_code': subject_code,
        'activity_group_code': class_type,
        'activity_code': class_id
    }

    response = session.post(enrol_subject_url, params=params, data=data)
    if response.status_code == 200:
        send_mail(subject='Updated the subject!', message_body='Updated the subject!')
        sys.exit(0)
    else:
        request_failed(response, message='Unable to register for subject.')


def check_classes_and_enrol(session, login_token, student_number, subject, class_type):
    pmp_tuts_url = BASE_URL + 'rest/student/' + student_number + '/subject/' + subject + '/group/' + class_type + \
        '/activities/'

    params = {'ss': login_token}

    response = session.get(pmp_tuts_url, params=params)

    if response.status_code == 200:
        classes = response.json()

        for class_key in sorted(classes.keys())[0:3]:
            if classes[class_key]['selectable'] == 'available':
                register_subject(session, login_token, student_number, class_key)
    else:
        raise requests.RequestException('Unable to fetch tutorials.')


def initialise_session(session):
    first_url = BASE_URL + 'student'

    response = session.get(first_url)
    if response.status_code != 200:
        request_failed(failed_response=response, message='Unable to initialise session')

    return session


def login(session, student_number, password):
    initialise_session(session)

    data = {'username': student_number,
            'password': password}

    login_url = BASE_URL + 'rest/student/login'

    response = session.post(login_url, data=data)
    if response.status_code == 200:
        print 'Login successful'
        return response.json()['token']
    else:
        request_failed(failed_response=response, message='Login failed.')


def main():
    if not has_env_variables():
        return

    student_number = os.environ['TIMETABLE_BOT_USERNAME']
    password = os.environ['TIMETABLE_BOT_PASSWORD']
    subject = os.environ['TIMETABLE_BOT_SUBJECT']
    class_type = os.environ['TIMETABLE_BOT_CLASS_TYPE']

    session = requests.Session()
    login_token = login(session, student_number, password)

    print 'Attempting to register if class becomes available.'
    while True:
        check_classes_and_enrol(session, login_token, student_number, subject, class_type)
        time.sleep(5)
        print 'Still attempting.'


if __name__ == '__main__':
    try:
        main()
    except:
        send_mail('Unexpectedly exited the script', 'Unexpected exited the script')
