# UTS Timetable Bot
TL;DR: Had to take Friday 4pm class, made bot that will enrol me in Thursday class if it becomes available.

## Data setup
1. From your favourite browser, inspect element, select the network tab, and go to the uts timetable login page.
If you're using Google Chrome make sure to select preserve log.
2. Login to the timetable app, and select the class for the subject that you'd like to change. 
3. From the list of network calls, select the network call to:
`aplus2017/rest/student/{student number}/subject/{subject code}/group/{class type}/activities/?ss={login token}`
4. Take note of the subject code, the class type, and the activity codes for the classes you'd like to enrol in.

## Script setup
1. Install python, pip, and virtualenvs. Virtualenvs is optional, skip to 4 if not using them.
2. Create the virtualenv `virtualenv  .venv`
3. `source .venv/bin/activate`
4. `pip install -r requirements.txt`
5. Edit the envs.sh with the appropriate values
6. `source envs.sh`
7. `python timetable_bot.py`
8. Wait for success (hopefully!)

For your own sanity, it might be worth checking that emails are working correctly by running `python trigger_mail.py`.
