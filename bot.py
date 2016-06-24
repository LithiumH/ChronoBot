import websockets
import asyncio
import requests
import json
import time
import pickle
import pymongo
from pymongo import MongoClient
from timeSheetMaker import *
from constants import *
from models.user import *
from chrono import *
from markov import get_conv, set_conv

class Listener(object):
    def __init__(self):
        # self.state = '' # state can be timesheet-init, or an empty string
        self.user_map = {}
        for u in get_all_user():
            u.previous_conv = []
            self.user_map[u.unique_id] = u
        print(self.user_map)

    def start(self):
        token = 'xoxb-53468281812-uwQohEw49nWfhcy8N2myHv8H'
        url = 'https://slack.com/api/rtm.start'
        response = requests.get(url + '?token=' + token)
        payload = json.loads(response.text)
        wws = payload['url']
        async def main():
            async with websockets.connect(wws) as websocket:
                self.websocket = websocket
                while True:
                    greeting = await websocket.recv()
                    event = json.loads(greeting)
                    print(event)
                    if 'type' in event and event['type'] == 'message' and event['user'] != 'U1KDS89PW':
                        text = event['text']
                        unique_id = event['user']
                        channel = event['channel']
                        ping = '<@{}> '.format(unique_id)
                        if event['channel'][0] == 'D':
                            ping = ''
                        if unique_id not in self.user_map:
                            if '<@U1KDS89PW>' in text or event['channel'][0] == 'D':
                                if 'register me' in text:
                                    user = User(unique_id)
                                    user.chrono = True
                                    self.user_map[unique_id] = user
                                    await websocket.send(self.make_json(channel, ping + 'What is your full name?'))
                                else:
                                    await websocket.send(self.make_json(channel, ping + \
                                            'You seem to not be in the database, please type "@chronobot register me".'))
                            continue
                        user = self.user_map[unique_id]
                        if '<@U1KDS89PW>' in text:
                            user.chrono = True
                        if user.chrono or event['channel'][0] == 'D':
                            step = user.step
                            if user.state == '':
                                user.state, new_text = self.switch_state(user, text, ping)
                                if new_text:
                                    await websocket.send(self.make_json(channel, new_text))
                            elif user.state == 'register me':
                                if step == 0:
                                    user.name = text
                                    await websocket.send(self.make_json(channel, ping + 'What is your email?'))
                                if step == 1:
                                    user.email = text
                                    print(text)
                                    await websocket.send(self.make_json(channel, ping + 'What is your manager\'s first name'))
                                elif step == 2:
                                    user.manager = text
                                    await websocket.send(self.make_json(channel, ping + 'What is your Team?'))
                                elif step == 3:
                                    user.team = text
                                    await websocket.send(self.make_json(channel, ping + 'What is your role?'))
                                elif step == 4:
                                    user.role = text
                                    user.start_date = datetime.datetime.utcnow()
                                    await websocket.send(self.make_json(channel, ping + \
                                            'Registration complete! Name: {}, Email: {}, Manager: {}, Team: {}, Role: {}'.format(
                                                user.name, user.email, user.manager, user.team, user.role)))
                                    user.state = ''
                                    user.chrono = False
                                    set_user(user.unique_id, user)
                                user.step += 1
                            elif user.state == 'timesheet-init':
                                if text == 'yes':
                                    date = datetime.date.today()
                                    new_date = closest_sunday(date)
                                    path = self.generate_default(user.name, user.role, new_date)
                                    send_email(user.name, user.email, new_date, 'myTimeSheet.xlsx', path, user.manager)
                                    await websocket.send(self.make_json(channel, ping + 'BOOM! Your timesheet is sent'))
                                else:
                                    args = text.split(' ')
                                    if len(args) != 6:
                                        await websocket.send(self.make_json(channel, ping + 'Sorry, wrong syntax. Please start over'))
                                    else:
                                        new_date = closest_sunday(date)
                                        path = generate_specific(user.name, new_date, user.role, args[0], args[1], args[2], args[3], args[4], args[5])
                                        date = datetime.datetime.strptime(args[0], '%m-%d-%Y')
                                        send_email(user.name, user.email, closest_sunday(date), 'myTimeSheet.xlsx', path, user.manager)
                                user.state = ''
                            elif user.state == 'quit':
                                for k,v in self.user_map.iteritems():
                                    set_user(u, v)
                                user.chrono = False
                                continue
                            if user.state == 'faq':
                                if text == 'no' and user.step == 6: # Using step as indicator of which state...
                                    await websocket.send(self.make_json(channel, ping + 'That\'s too bad.'))
                                    user.state = ''
                                elif 'yes' in text and user.step == 6:
                                    user.step = 10
                                    await websocket.send(self.make_json(channel, ping + 'What is the answer?'))
                                elif get_answer(text, 0.3) and user.step != 10:
                                    await websocket.send(self.make_json(channel, ping + get_answer(text, 0.5)))
                                    user.state = ''
                                elif user.step == 10:
                                    set_answer(user.question, text, user.name)
                                    await websocket.send(self.make_json(channel, ping + 'Thank you, I am now smarter.'))
                                    user.step = 0
                                    user.state = ''
                                    user.chrono = False
                                else:
                                    user.question = text
                                    user.step = 6
                                    await websocket.send(self.make_json(channel,
                                        'I do not have an answer to that question. Do you know the answer? (yes or no)'))
                            if user.state == 'random':
                                if text[0:4] == 'say:':
                                    set_conv(text[5:], *user.previous_conv)
                                    await websocket.send(self.make_json(channel, 'Ok I\'ll say that next time'))
                                user.state = ''
                                user.chrono = False
        asyncio.get_event_loop().run_until_complete(main())

    def get_user_name(self, internal_name):
        return self.user_map[internal_name]

    def generate_default(self, fullname, role, date):
        path = generate_specific(fullname, date, role, 8, 8, 8, 8, 8)
        return path

    def get_date_from_secs(self, epoch_secs):
        ts = time.gmtime(epoch_secs)
        mon, day, year = ts.tm_mon, ts.tm_mday, ts.tm_year
        if mon < 10:
            mon = '0' + str(mon)
        if day < 10:
            day = '0' + str(day)
        return '{0}-{1}-{2}'.format(mon, day, year)

    def make_json(self, channel, text):
        return json.dumps({'type':'message', 'text':text, 'channel':channel})

    def switch_state(self, user, text, name):
        state, new_text = '', ''
        if 'timesheet' in text:
            new_text = name + 'Would you like to use defaults? If not specify the date' + \
                    '[mm-dd-yyyy] and hours worked each day separated by spaces.'
            state = 'timesheet-init'
        elif 'quit' in text:
            new_text = 'Good bye.'
            state = 'quit'
        elif 'register me' in text:
            new_text = name + 'You have already registered...'
        elif text == 'What have you done today?':
            new_text = previous(user, random=True)
        elif text[len(text) - 1] == '?':
            state = 'faq'
        elif text[0:4] == 'log:':
            log_activity(user, text[5:])
            new_text = name + 'I have logged your journal'
        else:
            if text[0:3] != 'say':
                user.previous_conv += [text]
                if len(user.previous_conv) > 3:
                    user.previous_conv.pop(0)
                conv = get_conv(*user.previous_conv)
                if not conv:
                    new_text = name + 'I don\'t know what to say...'
                else:
                    new_text = name + conv
            state = 'random'
        return state, new_text

l = Listener()
l.start()


