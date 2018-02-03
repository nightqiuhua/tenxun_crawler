import urllib.parse 
import urllib.request 
import re 
from downloader import Downloader 
import datetime 
import time
from mongo_cache import MongoCache

def link_crawler(seed_url,link_regx=None,delay=5,user_agent='wswp',proxies=None,max_depth=-1,max_urls=-1,scrape_callback=None,num_retries=1,cache=None):
	crawl_queue =[seed_url]
	seen = {seed_url:0}
	D = Downloader(delay=delay,user_agent=user_agent,proxies=proxies,num_retries=num_retries,cache=cache)
	num_urls =0
	num = 0
	while crawl_queue:
		url = crawl_queue.pop()
		print('url=',url)
		depth = seen[seed_url]

		html = D(url).decode('utf-8')
		#print('html=',html)
		links=[]
		if depth !=max_depth:
			if scrape_callback:
				scrape_callback(url,html)

			if link_regx:
				links.extend(link for link in get_links(html) if re.match(link_regx,link))

			for link in links:
				link = 'position.php?'+link
				link = normalize(seed_url,link)
				if link not in seen:
					seen[link] = depth+1
					if same_domain(link,seed_url):
						crawl_queue.append(link)
						#print('crawl_queue=',crawl_queue)
		num +=1
		print('num=',num)
		num_urls +=1
		if num_urls == max_urls:
				break


def get_links(html):
	webpage_regex=re.compile('<a href="position.php\?(.*?)"',re.IGNORECASE)
	#print('webpage_regex.findall(html)=',webpage_regex.findall(html))
	return webpage_regex.findall(html)

def normalize(seed_url,link):
	link,_=urllib.parse.urldefrag(link)
	return urllib.parse.urljoin(seed_url,link)

def same_domain(url_1,url_2):
	return urllib.parse.urlparse(url_1).netloc == urllib.parse.urlparse(url_2).netloc

link_crawler('https://hr.tencent.com/position.php?keywords=python', 'keywords=python&start=', cache=MongoCache())




