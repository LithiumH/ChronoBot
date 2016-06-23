import pymongo
from pymongo import MongoClient
import datetime


client = MongoClient('localhost', 27017)
db = client.test
collection = db.test_collection

def log_activity(user, log):
	return log_activity_time(user, datetime.datetime.utcnow(), log)

def log_activity_time(user, date_time, log):
	post = {"author": user,
			"date": date_time,
			"log": log}
	post_id = collection.insert_one(post).inserted_id
	return post_id

def find_latest_datetime(user, date_time):
	date_beginning = datetime.datetime(date_time.year, date_time.month, date_time.day)
	posts = collection.find({"date" : {"$lt": date_time, "$gt": date_beginning}}).sort("date")
	latest = posts[posts.count() - 1]
	return latest

def find_latest(user):
	return find_latest_datetime(user, datetime.datetime.utcnow())



