class User(object):
	def __init__(self, unique_id):
		self.unique_id = unique_id
		self.name = ''
		self.role = ''
		self.manager = ''
		self.state = 'register me'
		self.step = 0