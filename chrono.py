import pymongo
from pymongo import MongoClient
import datetime
from similarity import similarity
from models.user import User


client = MongoClient('localhost', 27017)
db = client.interns
logs = db.logs
faq = db.faq
users = db.users

def log_activity(user, log):
    return log_activity_time(user, datetime.datetime.utcnow(), log)

def log_activity_time(user, date_time, log, start_date):
	dur = date_time - start_date
	post = {'author': user,
			'date': date_time,
			'duration': dur.days,
			'log': log}
	post_id = logs.insert_one(post).inserted_id
	return post_id

def previous(userid, date_time):
	user = get_user(userid)
	dur = date_time - user.start_date
	dur = dur.days
	if get_user(userid) != None:
		post = logs.find({'author': user.name, \
						   'team': user.team, \
						   'date': {'$lt': date_time, '$gt': user.start_date}}).sort({'date': -1}).limit(1)
	else:
		post1 = logs.find({'team': user.team, \
						   'duration': {'$gte': dur}}).sort({'duration': 1}).limit(1)
		post2 = logs.find({'team': user.team, \
						   'duration': {'$lte': dur}}).sort({'duration': -1}).limit(1)
		diff1 = post1[0]['duration'] - dur
		diff2 = dur - post2[0]['duration']
		if diff1 > diff2:
			post = post1
		else:
			post = post2
	return post

def find_latest(user):
    return find_latest_datetime(user, datetime.datetime.utcnow())

def find_latest_rand():
    return find_latest_datetime(None, datetime.datetime.utcnow())

def distance(q1, q2):
    if q1 == q2:
        return 0
    return similarity(q1, q2)

def get_answer(question, threshold=0.05):
	"""This function gets the closest answer to a question. The question param is a string
	This function returns None if there is not a question similar enough.
	"""
	cursor = faq.find()
	min_dist, best_post = float('inf'), None
	for post in cursor:
		new_dist = distance(question, post['question'])
		if new_dist < min_dist:
			min_dist, best_post = new_dist, post
	return best_post['answer'] if min_dist < threshold else None

def set_answer(question, answer, username):
	"""This function sets a question to an answer. user param means whoever answered it"""
	date_time = datetime.datetime.utcnow();
	cursor = faq.find({'question' : question})
	if cursor.count() > 0:
		update_result = faq.update_one({'question': question}, {
			'$set' : {
				'answer' : answer,
				'user' : username,
				'last_modified' : date_time}})
		return update_result.modified_count > 0
	post = {'question': question,
			'answer': answer,
			'last_modified': date_time,
			'user': username}
	post_id = faq.insert_one(post).inserted_id
	return True

def convert_to_map(user):
	pass

def convert_to_user(user_id, data_map):
	user = User(user_id)
	user.name = data_map['name']
	user.role = data_map['role']
	user.manager = data_map['manager']
	user.state = data_map['state']
	user.team = data_map['team']
	user.step = data_map['step']
	user.email = data_map['email']
	return user

def get_all_user():
	cursor = users.find()
	people = []
	for u in cursor:
		people += [convert_to_user(u['user_id'], u['data_map'])]
	return people

def get_user(user_id):
	cursor = users.find({'user_id' : user_id})
	if cursor.count() > 0:
		data_map = cursor[0]['data_map']
		return convert_to_user(user_id, data_map)
	return None

def set_user(user_id, user):
	data_map = {'name' : user.name,
			'role' : user.role,
			'manager' : user.manager,
			'state' : user.state,
			'team' : user.team,
			'step' : user.step,
			'email' : user.email}
	this_user = get_user(user_id)
	if this_user:
		update_result = users.update_one({'user_id' : user_id}, {
			'$set': {'data_map' : data_map}})
		return update_result.modified_count > 0
	post = {'user_id' : user_id,
			'data_map' : data_map}
	post_id = users.insert_one(post).inserted_id
	return True


