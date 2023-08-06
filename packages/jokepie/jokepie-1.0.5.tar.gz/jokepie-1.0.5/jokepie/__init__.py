import __main__
import requests as req
from difflib import SequenceMatcher
from datetime import datetime
import json
import string

class Joke:
	def __init__(self, category, jtype, joke, flags, id, safe, lang, req_obj):
		self.category = category
		self.joke_type = jtype
		self.joke = joke
		self.flags = flags
		self.id = id
		self.safe = safe
		self.language = lang
		self.lang = lang
		self.request = req_obj
		
	def get_joke(self):
		if self.joke_type == 'single':
			return self.joke[0]
		else:
			return {'setup': self.joke[0], 'delivery': self.joke[1]}
			
class Ping:
	def __init__(self, error=None, ts=None):
		self.error = error
		self.timestamp = ts
		
class InfoObject:
	def __init__(self, version=None, types=None, flags=None, jokecount=None, lang_jokecount=None, categories=None, timestamp=None):
		self.version = version
		self.categories = categories
		self.flags = flags
		self.joke_types = types
		self.joke_count = jokecount
		self.timestamp = timestamp
		
		self.cs_jokecount = self.get_parent_jokecount('fr', lang_jokecount)
		self.cs_jokecount = self.get_parent_jokecount('en', lang_jokecount)
		self.cs_jokecount = self.get_parent_jokecount('de', lang_jokecount)
		self.cs_jokecount = self.get_parent_jokecount('es', lang_jokecount)
		self.cs_jokecount = self.get_parent_jokecount('cs', lang_jokecount)
		self.cs_jokecount = self.get_parent_jokecount('pt', lang_jokecount)
		
	def get_parent_jokecount(self, lang, lis):
		if lis == None:
			return None
		for x in lis:
			if x['lang'] == lang:
				return x['count']
				
class Client:
	def __init__(self, raise_on_exc: bool=False):
		#super().__init__
		self.base_url = 'https://v2.jokeapi.dev/'
		self.raise_on_exc = raise_on_exc
		self.lang = {
		'english': 'en',
		'german': 'de',
		'czech': 'cz',
		'spanish': 'es',
		'french': 'fr',
		'portuguese': 'pt'
		}
		self.resp_codes = {
		200: 'Ok',
		201: 'Created',
		400: 'Bad Request',
		403: 'Forbidden',
		404: 'Not Found',
		413: 'Payload Too Large',
		414: 'URL Too Long',
		429: 'Too Many Requests',
		500: 'Internal Server Error',
		523: 'Origin Unreachable'
		}
		self.converter = self.Converter(self.lang)
		#Try to reach server by ping
		self.ping()
		
		#Aquire Optional Information
		self.InfoObj = self.info()
		self.version = self.InfoObj.version
		
		#Edit final information
		self.converter.categories = self.InfoObj.categories
		self.converter.flags = self.InfoObj.flags
		
	#Define Parent Errors
	class BadJoke(Exception):
		pass
		
	class ConnectionError(Exception):
		pass
		
	class ConnectionRefused(Exception):
		pass
	
	class InvalidInput(Exception):
		pass
	#Define Main Errors
	class BadArgument(InvalidInput):
		"""
		The argument that was provided is invalid!
		"""
		pass
	class BadRequest(BadJoke):
		"""
		The request you have sent to JokeAPI is formatted incorrectly and cannot be processed
		"""
		pass
	class Banned(BadJoke):
		"""
		You have been added to the blacklist due to malicious behavior and are not allowed to send requests to JokeAPI anymore
		"""
		pass
	class NotFound(BadRequest):
		"""
		The URL you have requested couldn't be found
		"""
		pass
	class LargeRequest(BadJoke):
		"""
		The payload data sent to the server exceeds the maximum size of 5120 bytes
		"""
		pass
	class BadURL(BadJoke):
		"""
		The URL exceeds the maximum length of 250 characters
		"""
		pass
	class ServerError(BadJoke):
		"""
		There was a general internal error within JokeAPI. You can get more info from the properties in the response text
		"""
		pass
	class ServerOffline(ServerError):
		"""
		Server is temporarily offline due to maintenance or a dynamic IP update. Please be patient in this case.
		"""
		pass
	class RateLimited(BadJoke):
		"""
		You have exceeded the limit of 120 requests per minute and have to wait a bit until you are allowed to send requests again
		"""
		pass
		
	#Subclasses
	class Converter():
		def __init__(self, lang_codes={}, cat_codes=[], flags=[]):
			self.lang = lang_codes
			self.categories = cat_codes
			self.flags = flags
			
		def _resp_to_joke_handler(self, respb, req_obj=None):
			rv = []
			if 'amount' in respb:
				for iter_joke in respb['jokes']:
					rv.append(self._resp_to_joke(iter_joke, req_obj))
			else:
				rv.append(self._resp_to_joke(respb, req_obj))
			return rv
			
		def _get_joke_by_type(self, respb):
			if respb['type'] == 'single':
				return respb['joke']
			elif respb['type'] == 'twopart':
				return [respb['setup'], respb['delivery']]
			else:
				raise Exception()
				
		def _resp_to_joke(self, respb, req_obj):
			rv = Joke(
			respb['category'],
			respb['type'],
			self._get_joke_by_type(respb),
			respb['flags'],
			respb['id'],
			respb['safe'],
			respb['lang'],
			req_obj)
			return rv
			
		def _get_from_categories(self, cat):
			inst_cat = [y for y in cat]
			obj = []
			for i in inst_cat:
				perc = {x: SequenceMatcher(None, i, x).ratio() for x in self.categories}
				k = list(perc.keys())[list(perc.values()).index(max(perc.values()))]
				obj.append(k)
			return obj
			
		def _get_from_flags(self, flag):
			inst_flag = [y for y in flag]
			obj = []
			for i in inst_flag:
				perc = {x: SequenceMatcher(None, i, x).ratio() for x in self.flags}
				k = list(perc.keys())[list(perc.values()).index(max(perc.values()))]
				obj.append(k)
			return obj
		
		def _conv_to_flag_dict(self, flags):
			dict_ = {
		"nsfw": False,
		"religious": False,
		"political": False,
		"racist": False,
		"sexist": False,
		"explicit": False
		}
			inst_flag = [y for y in flags]
			for i in inst_flag:
				perc = {x: SequenceMatcher(None, i, x).ratio() for x in self.flags}
				k = list(perc.keys())[list(perc.values()).index(max(perc.values()))]
				dict_[k] = True
			return dict_
			
		def _lang_to_abb(self, lang):
			k = self.lang[lang]
			return k
			
		def _get_lang(self, lang, abb=True):
			perc = {x: SequenceMatcher(None, lang, x).ratio() for x in self.lang}
			k = list(perc.keys())[list(perc.values()).index(max(perc.values()))]
			if abb:
				return self._lang_to_abb(k)
			return k
			
		def _get_by_perc(self, val_, iter_):
			perc = {x: SequenceMatcher(None, val_, x).ratio() for x in iter_}
			k = list(perc.keys())[list(perc.values()).index(max(perc.values()))]
			return k
			
		def _unix_to_datetime(self, unix_timestamp):
			dt = datetime.fromtimestamp(unix_timestamp / 1000)
			formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
			obj = datetime.strptime(formatted_time, '%Y-%m-%d %H:%M:%S.%f')
			return obj
			
	#Main Functions
	def HandleRespException(self, resp):
		resp_handle_table = {
		400: self.BadRequest,
		403: self.Banned,
		404: self.NotFound,
		413: self.LargeRequest,
		414: self.BadURL,
		429: self.RateLimited,
		500: self.ServerError,
		523: self.ServerOffline
		}
		respc = resp.status_code
		if respc in self.resp_codes:
			raise resp_handle_table[respc]
		else:
			raise self.BadJoke
			
	def info(self):
		resp = req.get(f'{self.base_url}/info')
		resp_body = resp.json()
		
		if resp_body['error'] is True:
			self.HandleRespException(resp)
			
		timestamp = self.converter._unix_to_datetime(resp_body['timestamp'])
		obj = InfoObject(resp_body['version'], resp_body['jokes']['types'], resp_body['jokes']['flags'], resp_body['jokes']['totalCount'], resp_body['jokes']['safeJokes'], resp_body['jokes']['categories'], timestamp)
		return obj
		
	def ping(self):
		resp = req.get(f'{self.base_url}/ping')
		resp_body = resp.json()
		
		obj = Ping(resp_body['error'], resp_body['timestamp'])
		return obj
		
	def get_joke(self, content: str='', lang: str='english', categories: list=['any'], blacklist=[], joke_type: str='single', safe_mode: bool=False, id_range: list=[], amount: int = 1) -> Joke:
		f_categories = self.converter._get_from_categories(categories)
		#https://v2.jokeapi.dev/joke/Programming,Misc?format=xml&blacklistFlags=nsfw,sexist&type=single&lang=ru&amount=2
		reqt = f'{self.base_url}/joke/{",".join(f_categories)}?format=json'
		if blacklist != []:
			f_flags = self.converter._get_from_flags(blacklist)
			reqt += f'&blacklistFlags={",".join(f_flags)}'
		if id_range != []:
			range_limit = self.InfoObj.joke_count
			if id_range[0] < 0 or x > (range_limit - 1):
				id_range[0] = 0
				if self.raise_on_exc == True:
					raise self.BadArgument
			if id_range[1] < 1 or x > range_limit:
				id_range[1] = range_limit
				if self.raise_on_exc == True:
					raise self.BadArgument
			reqt += f'&idRange={str(id_range[0])}-{str(id_range[1])}'
		if content != '':
			valid_chars = string.ascii_letters + string.digits + '.!,'
			if True not in [False if y in valid_chars else True for y in content]:
				reqt += f'&contains={content}'
			else:
				if self.raise_on_exc == True:
					raise self.BadArgument
		reqt += f'&type={self.converter._get_by_perc(joke_type, self.InfoObj.joke_types)}'
		if amount > 10:
			amount = 1
		reqt += f'&amount={amount}'
		reqt += f'&lang={self.converter._get_lang(lang)}'
		if safe_mode == True: reqt += f'&safe-mode'
		reqs = req.get(reqt)
		respb = reqs.json()
		if respb['error'] == True and respb['code'] == 106:
			return respb['causedBy'] if 'causedBy' in respb else -1
		if respb['error'] == True and self.raise_on_exc == True:
			if self.raise_on_exc == True:
				raise self.BadRequest
			else:
				return -1
		joke_obj = self.converter._resp_to_joke_handler(respb, reqs)
		if len(joke_obj) <= 1:
			return joke_obj[0]
		return joke_obj
		
	def upload_joke(self, joke: str or dict, category: str, joke_type: str='single', lang: str='english', on_flags: list=[]) -> bool:
		#https://v2.jokeapi.dev/submit
		jtype = self.converter._get_by_perc(joke_type, self.InfoObj.joke_types)
		payload = {
		"formatVersion": 3,
		"category": self.converter._get_by_perc(joke_type, self.InfoObj.categories),
		"type": jtype,
		"flags": self.converter._conv_to_flag_dict(on_flags),
		"lang": self.converter._get_lang(lang)
		}
		if jtype == 'single':
			payload['joke'] = joke
		else:
			payload['setup'] = joke[0]
			payload['delivery'] = joke[1]
		sreq = req.post(f'{self.base_url}submit?dry-run', data=json.dumps(payload), headers={})
		
		respb = sreq.json()
		if respb['error'] == True and self.raise_on_exc == True:
			raise self.BadRequest
		return respb['error']
