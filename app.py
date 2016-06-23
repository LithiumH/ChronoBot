from flask import Flask, request
from chrono import *

app = Flask(__name__)

@app.route("/")
def hello():
	return "Hello World"

@app.route('/generate', methods=['POST'])
def generate():
	return ''

@app.route('/log', methods=['POST'])
def log():
	return ''

@app.route('/register_intern', methods=['POST'])
def register():
	return ''


if __name__ == "__main__":
	app.run()
