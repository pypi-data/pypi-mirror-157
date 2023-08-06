import json
import requests
import time
import datetime
from .tools import getData,DATA
from ColorCraft import Color
from ColorCraft import Colors
from .Errors import *
try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO ## for Python 3

__all__ = ['Color', 'Colors', "Message", "DisWebhook", "Embed", "File"]
class DeletedMessage(object):
	def __init__(self, response):
		self.response = response
	def __repr__(self):
		return f"<DeletedMessage({self.response})>"
class DeletedWebhook(object):
	def __init__(self, response):
		self.response = response
	def __repr__(self):
		return f"<DeletedWebhook({self.response})>"

		

class File:
	def __init__(self, name,content=b"",path="",mode="r",encoding=None):
		super(File, self).__init__()
		self.name = name
		self.path = path
		self.content = content if content is not None else b""
		self.mode = mode
		if not content:
			try:
				self.file = open(str(self),mode=mode,encoding=encoding)
			except ValueError:
				self.file = open(str(self),mode=mode)
		else:
			self.file = StringIO(self.content)
	def read(self,mode="r",*args,**kw):
		with open(str(self),mode,*args,**kw) as f:
			self.content = f.read()
		return self.content
	def display(self):
		return repr(self)
	def __getattr__(self,name):
		return getattr(self.file,name)
	def __str__(self):
		return ((self.path+"\\" if self.path else "")+self.name)
	def __exit__(self):
		if not self.file.closed:self.file.close()
	def __repr__(self):
		clear = repr("_"+self.name)
		return f"<File(name={repr(self.name)},content={clear},mode={self.mode})>"


class Message:
	def __init__(self, message,data=None,json_data={}):
		super(Message, self).__init__()
		self.message = message
		self.ctx     = self.getData()
		self.url = self.filter(self.message)
		self.json_data = json_data
	def filter(self, url):
		return url.split('?')[0]
	def getData(self):
		self.url = self.filter(self.message)
		rq = requests.get(self.url)
		try:
			message_id = rq.json()['id']
		except KeyError as key:
			raise MessageError("fail to get message KeyError: {},data = {}".format(key,rq.json()))
		except Exception as error:
			raise MessageError("fail to get message Exception: {}".format(error))
		return rq
	def delete(self,timeout=None,proxies=None):
		print("deleting message:",self.url)
		response = requests.delete(self.url,proxies= proxies, params={'wait': True},
			timeout= timeout,json={})
		return DeletedMessage(response)
	def edit(self,content,timeout=None,proxies=None):
		patch_kwargs = {'json': {"content":content} if not bool(self.json_data) else self.json_data}
		response = requests.patch(self.url, proxies= proxies, params={'wait': True},
			timeout= timeout,json=patch_kwargs["json"])
		return Message(response.url,response.json())
	def __repr__(self):
		message = DATA( self.message,"Message" )
		ctx     = DATA( self.ctx    ,"Ctx"     ) if self.ctx  is not None else None
		return f"<Message(message={message},ctx={ctx})>"

class Embed:
	def __init__(self, title=None, description=None, **kwargs):
		self.title = title
		self.description = description
		self.url = kwargs.get("url")
		self.timestamp = self.set_timestamp(kwargs.get("timestamp"))
		self.color = kwargs.get("color")
		self.footer = kwargs.get("footer")
		self.image = kwargs.get("image")
		self.thumbnail = kwargs.get("thumbnail")
		self.video = kwargs.get("video")
		self.provider = kwargs.get("provider")
		self.author = kwargs.get("author")
		self.fields = kwargs.get("fields", [])
		self.set_color(self.color)
	def json(self):
		json = self.__dict__.copy()
		if json.get("color"):
			json["color"] = int(json["color"])
		else:
			json["color"] = None
		return json
	def set_title(self, title):
		self.title = title
	def set_description(self, description):
		self.description = description
	def set_url(self, url):
		self.url = url
	def set_timestamp(self, timestamp=None):
		if timestamp is None:
			timestamp = time.time()
		self.timestamp = str(datetime.datetime.utcfromtimestamp(timestamp))
	def set_color(self, color):
		if isinstance(color,str):
			self.color = Color(color,type="hex")
		elif isinstance(color,Color) or color is None:
			self.color = color
		else:
			raise UnownColor(f"Unown Color {color}:{color.__class__.__name__}")
	def set_author(self, **kwargs):
		self.author = {
			"name": kwargs.get("name"),
			"url": kwargs.get("url"),
			"icon_url": kwargs.get("icon_url")
		}
	def set_image(self, **kwargs):
		self.image = {
			"url": kwargs.get("url"),
			"height": kwargs.get("height"),
			"width": kwargs.get("width")
		}
	def set_footer(self, **kwargs):
		self.footer = {
			"text": kwargs.get("text"),
			"icon_url": kwargs.get("icon_url")
		}
	def set_thumbnail(self, **kwargs):
		self.thumbnail = {
			"url": kwargs.get("url"),
			"height": kwargs.get("height"),
			"width": kwargs.get("width")
		}
	def set_video(self, **kwargs):
		self.video = {
			"url": kwargs.get("url"),
			"height": kwargs.get("height"),
			"width": kwargs.get("width"),
		}
	def add_field(self,**kwargs):
		self.fields.append(
			{
				"name": kwargs.get("name"),
				"value": kwargs.get("value"),
				"inline": kwargs.get("inline", True)
			}
		)
	def remove_field(self,index):
		self.fields.pop(index)
	def replace_field(self,index,**kwargs):
		self.fields[index] = (
			{
				"name": kwargs.get("name"),
				"value": kwargs.get("value"),
				"inline": kwargs.get("inline", True)
			}
		)

class DisWebhook:
	def __init__(self, url, content=None, username=None, avatar_url=None, **kwargs):
		data,r           = getData(url)
		if r.status_code in [200,204]:
			self.default_web = data
		else:
			try:
				raise WebhookError(data["message"])
			except KeyError:
				raise WebhookError(data)
		self.url         = url
		self.content     = content
		self.id          = data["id"]
		self.avatar_url  = data["avatar"] 
		self.embeds      = []
		self.files       = {}
		self.proxies = kwargs.get("proxies",None)
		self.timeout = kwargs.get("timeout",None)
		self.  tts   = kwargs.get(  "tts"  ,None)
		# type check value :-: chack username value if is str or None
		# if None the default value will be the webhook name
		# if str that will be the new webhook name
		if username and isinstance(username,str): self.username= username
		elif username is None:					  self.username= data["name"]
		else: raise TypeError(f"expected str but get ('{username.__class__.__name__}')"\
			" make username 'None' for default name")
		# type check value :-: chack username value if is str or None
		# if None the default value will be the webhook name
		# if str it will be the new webhook avatar
		if avatar_url and isinstance(avatar_url,str): self.avatar_url= avatar_url
		elif avatar_url is None:					  self.avatar_url= data["avatar"]
		else: raise TypeError(f"expected str but get ('{avatar_url.__class__.__name__}')"\
				" make avatar_url 'None' for default avatar")

	def add_file(self, file,name=None):
		name = file.name if name is None else name
		if isinstance(file,File):
			self.files["{}".format(name)] = (name, file.content)
	def remove_file(self, file,name=None):
		if isinstance(file,str):
			filename = "{}".format(file if name is None else name)
		else:
			filename = "{}".format(file.name if name is None else name)
		if filename in self.files:
			del self.files[filename]
	def request(self,url):
		if bool(self.files) is False:
			response = requests.post(url, json=self.json, proxies=self.proxies,
									params={'wait': True},
									timeout=self.timeout)
		else:
			self.files["payload_json"] = (None, json.dumps(self.json))
			response = requests.post(url, files=self.files,
									proxies=self.proxies,
									timeout=self.timeout)
		return response
	def delete(self,timeout=None,proxies=None):
		response = requests.delete(self.url,proxies= proxies, params={'wait': True},
			timeout= timeout)
		return DeletedWebhook(response)
	def send(self,content=None,embed=None,embeds=[],files=[],**kwargs):
		exEmbeds = embeds
		embeds = []
		self.files   = files if files else self.files 
		self.proxies = kwargs.get("proxies",self.__dict__.get("proxies"))
		self.timeout = kwargs.get("timeout",self.__dict__.get("timeout"))
		self.tts     = kwargs.get(  "tts"  ,self.__dict__.get(  "tts"  ))
		if embed and isinstance(embed,Embed):
			embeds.append(embed.json())
		if bool(exEmbeds):
			for embed in exEmbeds:
				if isinstance(embed,Embed):
					embeds.append(embed.json())
				else:
					embeds.append(embed)

		url = self.url
		data = {
			"content": self.content if content is None else str(content),
			"username": self.username,
			"avatar_url": self.avatar_url,
			"tts"       : self.tts,
			"embeds": embeds
		}
		self.json = data
		rq = self.request(self.url)
		if 200 <= rq.status_code < 300:
			message = url+"/messages/"+rq.json()['id']
			return Message(message,json_data=self.json)
		else:
			raise WebhookError(f"Exception response status_code {rq.status_code} json:\n{rq.json()}")

	def __repr__(self):
		return f"<DisWebhook(username={repr(self.username)},id={self.id})>"

