import pymongo
from pymongo import MongoClient
import datetime
from similarity import similarity
from models.user import User

client = MongoClient('localhost', 27017)
db = client.interns
convs = db.convs

conv = {'c3' : '', 'c2' : '', 'c1' : 'how are you', 'response' : {'I\'m fine':1}}
post_id = convs.insert_one(conv).inserted_id

def get_conv(p3='', p2='', p1=''):
	cursor = convs.find({'p3':p3, 'p2':p2, 'p1':p1})

def set_conv(response, p3='', p2='', p1=''):
	post = {'p3':p3, 'p2':p2, 'p1':p1, {response}}
	update_result = convs.insert_one(post).inserted_id
	return True
