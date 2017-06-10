from bs4 import BeautifulSoup
from pprint import pprint 
import urllib
import json 
import time

DESTINATION_URL = "https://www.saseeding.org"
MTB_EVENT_TYPE = "3148f509-b19f-11e5-907e-08002773d9e3"
YEARS = [2017, 2016]


def scrape():
	 mtb_events = get_mtb_events()
	 for event in mtb_events: 
	  	categories = get_categories(mtb_events[event][0])
	  	time.sleep(2)



def get_mtb_events(): 
	events = {}
	for year in YEARS: 
		url = ("%s/participants/event-results/fetch-series-by-type?event_type=%s&event_year=%d" % 
			  (DESTINATION_URL, MTB_EVENT_TYPE, year))
		page = urllib.request.urlopen(url)
		content =  page.read().decode("utf-8")
		json_content = json.loads(content)
		soup = BeautifulSoup(json_content['HTML'], "html.parser")
		anchors = soup.find_all('a')
		
		for anchor in anchors: 
			event_reference = anchor["href"]
			divs = anchor.find_all('div')
			for div in divs:
				if ("event-date" in div["class"]):
					event_date = (div.find(text=True))
				elif ("event-title" in div["class"]):
					event_name = (div.find(text=True))
			events[event_name] = [event_reference, event_date]
	return events	

def get_categories(event_reference):
	categories = {}
	url =  (DESTINATION_URL + event_reference)
	page = urllib.request.urlopen(url)
	soup = BeautifulSoup(page, "html.parser")
	category_div = soup.find('div', attrs={"id" : "category_container"})

	#Check to see if event has categories first
	if category_div:
		divs = category_div.find_all('div')
		for div in divs: 
			if div.has_attr("data-event-category-id"):
				category_id = div["data-event-category-id"]
				category_name = div["data-loading-text"]
				category_stage_id = div["data-event-stage-id"]
				if (div["data-multiple-event-stages"] == "1"):
					category_multistage = True
				else: 
					category_multistage = False
				categories[category_name] = [category_id, category_multistage]
	return categories



scrape()
