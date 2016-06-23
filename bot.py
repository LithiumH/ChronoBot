import websockets
import asyncio
import requests
import json
import time
import datetime
from timeSheetMaker import *
from constants import *


class Listener(object):
	def __init__(self):
		self.state = '' # state can be timesheet-init, or an empty string
		self.user_map = user_map

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
					message = json.loads(greeting)
					print(message)
					if 'type' in message and message['type'] == 'message' and message['user'] in self.user_map:
						text = message['text']
						name = self.get_user_name(message['user'])
						channel = message['channel']
						if '<@U1KDS89PW>' in text and not self.state:
							new_text, self.state = self.switch_state(text)
							await websocket.send(self.make_json(channel, new_text))
						elif self.state == 'timesheet-init':
							if text == 'yes':
								date = datetime.date.today()
								path = self.generate_default(name, '{0}-{1}-{2}'.format(date.month, date.day, date.year))
								send_email(lastday(date, 'sunday'), 'myTimeSheet.xlsx', path)
								await websocket.send(self.make_json(channel, 'BOOM! Your timesheet is sent'))
							else:
								args = text.split(' ')
								if len(args) != 6:
									await websocket.send(self.make_json(channel, 'Sorry, wrong syntax. Please start over'))
								else:
									path = generate_specific(name, args[0], args[1], args[2], args[3], args[4], args[5])
									date = datetime.datetime.strptime(args[0], '%m-%d-%Y')
									send_email(name, lastday(date, 'sunday'), 'myTimeSheet.xlsx', path)
									await websocket.send(self.make_json(channel, 'BOOM! Your timesheet is sent'))
							self.state = ''
						elif self.state == 'register me':
							pass # TODO



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

	def switch_state(self, text):
		state = ''
		if 'timesheet' in text:
			new_text = 'Would you like to use defaults? If not specify the date' + \
					'[mm-dd-yyyy] and hours worked each day separated by spaces.'
			state = 'timesheet-init'
		elif 'register me' in text:
			new_text = 'What is your full name?'
			state = 'register me'
		else:
			new_text = 'Sorry I\'m too dumb to understand'
		return state, new_text


l = Listener()
l.start()


