import os
from os import path
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import random
import argparse
import requests
from pyquery import PyQuery as pq
import json
import pandas as pd
###########################################
if path.exists("proxies.txt") :
	with open("proxies.txt","r") as f:
		lines = f.readlines()
	for l in lines:
		proxies.append(l.strip())
	print("proxies = {}".format(proxies))
else:
	print("proxies.txt file is not exist!!")
	print("Caution: you're using your own machine proxy")
##
parser = argparse.ArgumentParser()
parser.add_argument("-k","--keyword", help="Enter a keyword to search")
parser.add_argument("-p","--page_limit", help="page count to limit the results",type=int,default=5)
args = parser.parse_args()
keyword = "".join(args.keyword)
page_limit = args.page_limit
##
software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=500)
data = []
table = []
proxies =  []
page_count = 0
##
url = 'https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={}&btnG='.format(keyword)
##
while 1:
	count = 0
	while 1 :
		try:
			count+=1
			if len(proxies) > 0:
				res = requests.get(url , headers={'user-agent': user_agent_rotator.get_random_user_agent(),} , proxies={"http": f"http://{random.choice(proxies)}" , "https": f"http://{random.choice(proxies)}"})
			else:
				res = requests.get(url , headers={'user-agent': user_agent_rotator.get_random_user_agent(),} )
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
	url = selector('[align="left"] a').attr('href')
	selector = selector('.gs_r.gs_or.gs_scl').items()
	if selector==0:
		break
	for sub_selector in selector:
		name = sub_selector('.gs_rt').text().replace("[PDF]","").replace("[HTML]","").replace("[BOOK]","").replace("[B]","").replace("[CITATION]","").replace("[C]","").strip()
		##
		href = sub_selector('.gs_rt a').attr('href')
		if href is None:
			href = sub_selector('.gs_or_ggsm a').attr('href')

		if href != None:
			av = 'yes'	#Availability
		else:
			av = 'no'
		##
		data = sub_selector('.gs_a').text().replace(" - ",",").split(",")
		author = ", ".join(data[:-2])
		# publisher = data[-1].split()[-1]
		# publish_date = data[-1].split()[0]
		publisher = data[-1] 
		publish_date = data[-2]
		# publish_date = data[-2] if str(data[-2]).isnumeric() else data[-3]
		##
		if "pdf" in str(href):
			link_type = "PDF"
			res_type = "pdf"
		elif "book" in str(href):
			link_type = "HTML"
			res_type = "book"
		else:
			link_type = "HTML" if av is 'yes' else None
			res_type = "article" if link_type!=None else None
		##		
		data = sub_selector('.gs_fl').text().split()
		try:
			cited = data[(data.index("Cited"))+2]
		except:
			cited = None
		##
		item = {
			'title':name,
			'authors':author,
			'publish year':publish_date,
			'Cited by #':cited,
			'type':res_type,
			'publisher':publisher,
			'link_type':link_type,			
			'free to access':av,
			'link':href,
		}
		table.append(item)
	
	if url!=None:
		url = "https://scholar.google.com"+str(url)
		page_count += 1
	else :
		print("break ###")
		break

	if page_count == int(page_limit):
		break

df = pd.json_normalize(table)
df_transposed = df.transpose()
# df.to_excel('df__a.xlsx')
file_name = keyword.replace(" ", "_") + ".csv"
df_transposed.to_csv(file_name)