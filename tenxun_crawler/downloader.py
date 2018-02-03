import urllib.parse 
import urllib.request 
import random
import re 
import socket 
from datetime import timedelta,datetime
import time 



DEFAULT_AGENT = 'wswp'
DEFAULT_DELAY = 5
DEFAULT_TIMEOUT = 60
DEFAULT_RETRIES = 1

class Throttle:
	def __init__(self,delay):
		self.delay = delay 
		self.domains = {}

	def wait(self,url):
		domain = urllib.parse.urlparse(url).netloc
		last_accessed = self.domains.get(domain)

		if self.delay > 0 and last_accessed is not None:
			sleep_secs = self.delay-(datetime.now()-last_accessed).seconds
			if sleep_secs > 0:
				time.sleep(sleep_secs)
		self.domains[domain] = datetime.now()

class Downloader:
	def __init__(self,delay=DEFAULT_DELAY,user_agent=DEFAULT_AGENT,proxies=None,num_retries=DEFAULT_RETRIES,timeout=DEFAULT_TIMEOUT,cache=None,opener=None):
		socket.setdefaulttimeout(DEFAULT_TIMEOUT)
		self.throttle = Throttle(delay)
		self.user_agent = user_agent 
		self.proxies = proxies
		self.num_retries = num_retries 
		self.timeout = timeout 
		self.opener = opener
		self.cache = cache

	def __call__(self,url):
		result = None 
		if self.cache:
			try:
				result = self.cache[url]
			except KeyError:
				pass
			else:
				if self.num_retries > 0 and 500 <= result['code']<600:
					result = None

		if result is None:
			self.throttle.wait(url)
			proxy = random.choice(self.proxies) if self.proxies else None
			headers = {'User-agent':self.user_agent}
			result = self.download(url,headers,proxy=proxy,num_retries=self.num_retries)
			if self.cache:
				self.cache[url] = result
		return result['html']

	def download(self,url,headers,proxy,num_retries,data=None):
		print('Download:',url)
		request = urllib.request.Request(url) or {}
		opener = self.opener or urllib.request.build_opener()
		if proxy:
			proxy_params={urllib.parse.urlparse(url).scheme:proxy}
			opener.add_handler(urllib.request.ProxyHandler(proxy_params))

		try:
			response = opener.open(url)
			html = response.read()
			code = response.code
		except urllib.error.URLErrors as e:
			print('Download error',e.reason)
			html=''
			if hasattr(e,'code'):
				code = e.code
				if num_retries >0 and 500<= code <600:
					html = self.download(url,headers,proxy,num_retries-1)
			else:
				code = None
		return {'html':html,'code':code}



