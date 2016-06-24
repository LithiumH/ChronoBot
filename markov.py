import pymongo
from pymongo import MongoClient
import datetime
from similarity import similarity
from models.user import User
import random as rand

client = MongoClient('localhost', 27017)
db = client.interns
convs = db.convs

# conv = {'p3' : '', 'p2' : '', 'p1' : 'how are you', 'response' : 'I\'m fine'}
# post_id = convs.insert_one(conv).inserted_id

def get_conv(p1='', p2='', p3=''):
	cursor = convs.find({'p1':p1, 'p2':p2, 'p3':p3})
	if (cursor.count() > 0):
		index = rand.randint(0, cursor.count()-1)
		return cursor[index]['response']
	cursor = convs.find({'p1':'', 'p2':p2, 'p3':p2})
	if (cursor.count() > 0):
		index = rand.randint(0, cursor.count()-1)
		return cursor[index]['response']
	cursor = convs.find({'p1':'', 'p2':'', 'p3':p3})
	if (cursor.count() > 0):
		index = rand.randint(0, cursor.count()-1)
		return cursor[index]['response']
	return None

def set_conv(response, p1='', p2='', p3=''):
	post = {'p3':p3, 'p2':p2, 'p1':p1, 'response':response}
	update_result = convs.insert_one(post).inserted_id
	return True
