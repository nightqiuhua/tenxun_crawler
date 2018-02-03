import re
import urllib.request

def scrape(html):
	area = re.findall('<a href="position.php\?(.*?)"',html)
	#area = re.findall('<tr id="places_area__row">.*?<td\s*class=["\']w2p_fw["\']>(.*?)</td>', html)[0]
	print('area=',area)
	print('len(area)',len(area))
	return area

html=urllib.request.urlopen('https://hr.tencent.com/position.php?keywords=python').read().decode('utf-8')
print('html=',html)
print('area=',scrape(html))