from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import random
software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=500)
data = []
URLs = None
counter = 1
postIds = ''
JSON_data = []
comments = []
posts = []
authors = []
table = []
page_num = 0


# proxies =  ["183.89.169.252:8080","178.252.80.226:34730","109.224.55.10:34082"]
proxies =  ["178.252.80.226:34730"]


import requests
from pyquery import PyQuery as pq
import json
import pandas as pd
url = 'https://scholar.google.com/citations?hl=en&view_op=search_authors&mauthors=a&btnG='
while 1:
	#res = requests.get(url)
	#print(url)
	count = 0
	while 1 :
		try:
			count+=1
			res = requests.get(url , headers={'user-agent': user_agent_rotator.get_random_user_agent(),} , proxies={"http": f"http://{random.choice(proxies)}" , "https": f"http://{random.choice(proxies)}"})
			print(url)
			print(res)
			print('#####')
			if res.status_code==200:
				break
		except:
			if count==10:
				break
			pass

	selector=pq(res.text)
	url = selector('[aria-label="Next"]').attr('onclick')
	selector = selector('.gsc_1usr').items()
	if selector==0:
		break
	for sub_selector in selector:
		name = sub_selector('.gs_ai_name').text()
		href = sub_selector('.gs_ai_name a').attr('href')
		if href !=None:
			href = 'https://scholar.google.com'+href
		aff = sub_selector('.gs_ai_aff').text()
		eml = sub_selector('.gs_ai_eml').text().replace('Verified email at ','')
		cby = sub_selector('.gs_ai_cby').text().replace('Cited by ','')
		tags = ', '.join([x.text() for x in sub_selector('.gs_ai_int a').items()])
		item = {
			'name':name,
			'href':href,
			'aff':aff,
			'eml':eml,
			'cby':cby,
			'tags':tags,
		}
		#print(ut)
		table.append(item)
	if url!=None:
		url = url.replace("window.location='",'https://scholar.google.com').replace(r'\x26','&').replace(r'\x3d','=').strip("'")
		page_num += 1
	else :
		break

	if page_num == 2:
		break

df = pd.json_normalize(table)
df.to_excel('test.xlsx')