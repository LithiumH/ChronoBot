import pymongo
from pymongo import MongoClient
import datetime


client = MongoClient('localhost', 27017)
db = client.interns
logs = db.logs
faq = db.faq

def log_activity(user, log):
	return log_activity_time(user, datetime.datetime.utcnow(), log)

def log_activity_time(user, date_time, log):
	post = {'author': user,
			'date': date_time,
			'log': log}
	post_id = logs.insert_one(post).inserted_id
	return post_id

def find_latest_datetime(user, date_time):
	date_beginning = datetime.datetime(date_time.year, date_time.month, date_time.day)
	if user:
		posts = logs.find({'author' : user, \
				'date' : {'$lt': date_time, '$gt': date_beginning}}).sort('date')
	else:
		posts = logs.find({'date' : {'$lt': date_time, '$gt': date_beginning}})
								.sort('date')
	latest = posts[posts.count() - 1]
	return latest

def find_latest(user):
	return find_latest_datetime(user, datetime.datetime.utcnow())

def find_latest_rand():
	return find_latest_datetime(None, datetime.datetime.utcnow())

def distance(q1, q2):
	if q1 == q2:
		return 0
	return float('inf')

def get_answer(question, threshold=3):
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

def set_answer(question, answer, user):
	"""This function sets a question to an answer. user param means whoever answered it"""
	date_time = datetime.datetime.utcnow();
	cursor = faq.find({'question' : question})
	if cursor.count() > 0:
		update_result = faq.update_one({'question': question}, {
			'$set' : {
				'answer' : answer,
				'user' : user,
				'last_modified' : date_time}})
		return update_result.modified_count() > 0
	post = {'question': question,
			'answer': answer,
			'last_modified': date_time,
			'user': user}
	post_id = faq.insert_one(post).inserted_id
	return True

