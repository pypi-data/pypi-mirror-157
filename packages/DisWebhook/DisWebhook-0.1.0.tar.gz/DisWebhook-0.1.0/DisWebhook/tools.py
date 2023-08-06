import requests

class DATA(object):
	def __init__(self, data, name):
		super(DATA, self).__init__()
		self.data,self.name = data,name
	def __repr__(self):
		return f"<data(data={repr(self.name)})>"

def getData(url):
	response = requests.get(url)
	data = response.json()
	return data,response