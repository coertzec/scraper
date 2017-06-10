from bs4 import BeautifulSoup
from pprint import pprint 
import urllib
import json 

MTB_EVENT_TYPE = "3148f509-b19f-11e5-907e-08002773d9e3"
YEARS = [2017, 2016]


def scrape():
	#get_mtb_events()
	get_categories()

def get_mtb_events(): 
	events = {}
	for year in YEARS: 
		url = "https://www.saseeding.org/participants/event-results/fetch-series-by-type?event_type=%s&event_year=%d" % (MTB_EVENT_TYPE, year)
		page = urllib.request.urlopen(url)
		content =  page.read().decode("utf-8")
		json_content = json.loads(content)
		soup = BeautifulSoup(json_content['HTML'], "html.parser")
		anchors = soup.find_all('a')
		for anchor in anchors: 
		 	divs = anchor.find_all('div')
		 	for div in divs: 
		 		if ("event-date" in div["class"]):
		 			event_date = (div.find(text=True))
		 		elif ("event-title" in div["class"]):
		 			event_name = (div.find(text=True))
		 	events[event_name] = event_date
	return events	

def get_categories():
	categories = {}
	url = "https://www.saseeding.org/participants/event-results/pe-to-plett-mtb-2017-03-02"
	page = urllib.request.urlopen(url)
	soup = BeautifulSoup(page, "html.parser")
	category_div = soup.find('div', attrs={"id" : "category_container"})
	pprint(category_div)



scrape()
