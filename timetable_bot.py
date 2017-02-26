import requests
import os
import sys
import time

from utils import request_failed, has_env_variables, send_smtp_mail

BASE_URL = 'https://mytimetable.uts.edu.au/aplus2017/'


def send_mail(subject, message_body):
    """
    Sends a notification email with the specified subject and message body.
    :param subject: message subject
    :param message_body: message content
    :return:
    """
    smtp_server = os.environ['GMAIL_SMTP_SERVER']
    smtp_server_port = os.environ['GMAIL_SMTP_SERVER_PORT']
    sender_email = os.environ['GMAIL_USERNAME']
    sender_password = os.environ['GMAIL_PASSWORD']
    recipient_email = os.environ['TIMETABLE_BOT_TO_EMAIL']

    send_smtp_mail(smtp_server, smtp_server_port, sender_email, sender_password, recipient_email, subject, message_body)


def register_subject(session, login_token, student_code, class_key):
    """
    Registers the user for a specific class.
    :param session: authenticated request.Session object
    :param login_token: login token
    :param student_code: student number
    :param class_key: class details in the form "{subject code}|{class type}|{activity code}" e.g.
    "31927_SPR_U_1_S|Cmp1|02"
    :return:
    """
    enrol_subject_url = BASE_URL + 'rest/student/changeActivity/'
    params = {'ss': login_token}

    class_key_split = class_key.split('|')

    subject_code = class_key_split[0]
    class_type = class_key_split[1]
    class_id = class_key_split[2]

    data = {
        'token': 'a',  # I have no idea why this needs to be sent.
        'student_code': student_code,
        'subject_code': subject_code,
        'activity_group_code': class_type,
        'activity_code': class_id
    }

    response = session.post(enrol_subject_url, params=params, data=data)
    if response.status_code == 200:
        print 'Updated the subject. Successfully registered for: %s.' % class_key
        print 'Sending email notification now.'
        send_mail(subject='Updated the subject!', message_body='Updated the subject!')
        sys.exit(0)
    else:
        request_failed(response, message='Unable to register for subject.')


def check_classes_and_enrol(session, login_token, student_number, subject, class_type, activity_codes):
    """
    Pings the server and sees if the desired class has an availability. If available, student will be enrolled.
    :param session: authenticated request.Session object
    :param login_token: login token
    :param student_number: student number
    :param subject: subject number (not just the subject code, includes other stuff: e.g. 31927_SPR_U_1_S)
    :param class_type: the class type e.g. computer lab, tutorial e.g. Tut1, Cmp1
    :param activity_codes: the individual class ids for the class_type e.g. 01, 02 (must be zero padded)
    :return:
    """
    pmp_tuts_url = BASE_URL + 'rest/student/' + student_number + '/subject/' + subject + '/group/' + class_type + \
        '/activities/'

    params = {'ss': login_token}

    response = session.get(pmp_tuts_url, params=params)

    if response.status_code == 200:
        classes = response.json()

        availabilities = ''
        for class_key in sorted(classes):
            class1 = classes[class_key]
            if class1['activity_code'] in activity_codes:
                if class1['selectable'] == 'available':
                    register_subject(session, login_token, student_number, class_key)
                availabilities += 'Activity code %s: %s   ' % (class1['activity_code'], class1['selectable'])
        print availabilities
    else:
        raise requests.RequestException('Unable to fetch tutorials.')


def initialise_session(session):
    """
    Initialises a session with the uts server. (Not 100% sure if this is required).
    """
    first_url = BASE_URL + 'student'

    response = session.get(first_url)
    if response.status_code != 200:
        request_failed(failed_response=response, message='Unable to initialise session')

    return session


def login(session, student_number, password):
    """
    Logs the user in and returns a login token which is used as a GET parameter for further requests.
    """
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
    activity_codes = os.environ['TIMETABLE_BOT_ACTIVITY_CODES'].split(',')

    session = requests.Session()
    login_token = login(session, student_number, password)

    print 'Attempting to register if class becomes available.'
    while True:
        check_classes_and_enrol(session, login_token, student_number, subject, class_type, activity_codes)
        time.sleep(5)
        print 'Still attempting.'


if __name__ == '__main__':
    main()
    try:
        main()
    except KeyboardInterrupt:
        # Don't want to send an email if the user ctrl+c exits the script.
        pass
    except:
        print 'Unexpectedly exited the script.'
        send_mail('Unexpectedly exited the script', 'Unexpected exited the script')
