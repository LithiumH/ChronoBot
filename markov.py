import pymongo
from pymongo import MongoClient
import datetime
from similarity import similarity
from models.user import User

client = MongoClient('localhost', 27017)
db = client.interns
convs = db.convs

ponv = {'p3' : '', 'p2' : '', 'p1' : 'how are you', 'response' : 'I\'m fine'}
post_id = convs.insert_one(conv).inserted_id

def get_conv(p3='', p2='', p1=''):
	cursor = convs.find({'p3':p3, 'p2':p2, 'p1':p1})
	cursor
	for doc in cursor:
		res = doc['response']
		if res in answers_map:
			answers_map[res] += 1
		else:
			answer_map[res] = 1



def set_conv(response, p3='', p2='', p1=''):
	post = {'p3':p3, 'p2':p2, 'p1':p1, {response}}
	update_result = convs.insert_one(post).inserted_id
	return True
