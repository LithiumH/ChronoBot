import websockets
import asyncio
import requests
import json
import time
import datetime
import pickle
import pymongo
from pymongo import MongoClient
from timeSheetMaker import *
from constants import *
from models.user import *
from chrono import *

class Listener(object):
    def __init__(self):
        # self.state = '' # state can be timesheet-init, or an empty string
        self.chrono = False
        self.user_map = {}

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
                    if 'type' in event and event['type'] == 'message':
                        text = event['text']
                        if '<@U1KDS89PW>' in text or event['channel'] == 'D1KDUJZFG':
                            self.chrono = True
                        if self.chrono:
                            unique_id = event['user']
                            channel = event['channel']
                            ping = '<@{}> '.format(unique_id)
                            if event['channel'] == 'D1KDUJZFG':
                                ping = ''
                            if unique_id not in self.user_map:
                                if 'register me' in text:
                                    self.user_map[unique_id] = User(unique_id)
                                    await websocket.send(self.make_json(channel, ping + 'What is your full name?'))
                                else:
                                    await websocket.send(self.make_json(channel, ping + 'You seem to not be in the database, please type register me.'))
                            else:
                                user = self.user_map[unique_id]
                                step = user.step
                                if user.state == '':
                                    user.state, new_text = self.switch_state(text, ping)
                                    await websocket.send(self.make_json(channel, new_text))
                                elif user.state == 'register me':
                                    if step == 0:
                                        user.name = text
                                        await websocket.send(self.make_json(channel, ping + 'What is your email?'))
                                    if step == 1:
                                        user.email = text
                                        await websocket.send(self.make_json(channel, ping + 'What is your manager\'s first name'))
                                    elif step == 2:
                                        user.manager = text
                                        await websocket.send(self.make_json(channel, ping + 'What is your Team?'))
                                    elif step == 3:
                                        user.team = text
                                        await websocket.send(self.make_json(channel, ping + 'What is your role?'))
                                    elif step == 4:
                                        user.role = text
                                        await websocket.send(self.make_json(channel, ping + 'Registration complete! Name: {}, Email: {}, Manager: {}, Team: {}, Role: {}'.format(user.name, user.email, user.manager, user.team, user.role)))
                                        user.state = ''
                                    user.step += 1
                                elif user.state == 'timesheet-init':
                                    if text == 'yes':
                                        date = datetime.date.today()
                                        new_date = lastday(date, 'sunday')
                                        path = self.generate_default(user.name, new_date)
                                        send_email(user.name,new_date, 'myTimeSheet.xlsx', path, user.manager)
                                        await websocket.send(self.make_json(channel, ping + 'BOOM! Your timesheet is sent'))
                                    else:
                                        args = text.split(' ')
                                        if len(args) != 6:
                                            await websocket.send(self.make_json(channel, ping + 'Sorry, wrong syntax. Please start over'))
                                        else:
                                            path = generate_specific(user.name, args[0], args[1], args[2], args[3], args[4], args[5])
                                            date = datetime.datetime.strptime(args[0], '%m-%d-%Y')
                                            send_email(user.name, lastday(date, 'sunday'), 'myTimeSheet.xlsx', path, user.manager)
                                    user.state = ''
                                elif user.state == 'quit':
                                    pass
                                elif user.state == 'faq':
                                    await websocket.send(self.make_json(channel, ping + get_answer(text)))

        asyncio.get_event_loop().run_until_complete(main())

    def get_user_name(self, internal_name):
        return self.user_map[internal_name]

    def generate_default(self, fullname, date):
        path = generate_specific(fullname, date, 8, 8, 8, 8, 8)
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

    def switch_state(self, text, name):
        state = ''
        if 'timesheet' in text:
            new_text = name + 'Would you like to use defaults? If not specify the date' + \
                    '[mm-dd-yyyy] and hours worked each day separated by spaces.'
            state = 'timesheet-init'
        elif 'register me' in text:
            new_text = name + 'You have already registered...'
        elif text[len(text) - 1] == '?':
            new_text = name + 'I noticed you sent a question, let me think...'
            state = 'faq'
        else:
            new_text = name + 'Sorry I\'m too dumb to understand'
        return state, new_text

l = Listener()
l.start()


