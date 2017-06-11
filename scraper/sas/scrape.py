from bs4 import BeautifulSoup
from pprint import pprint 
from scraper.sas.sas_models import SASEvent, SASCategory, SASCategoryStage
from scraper.base_models.models import Event, Category, CategoryStage
from scraper import db
from datetime import datetime
import urllib
import json 
import time


DESTINATION_URL = "https://www.saseeding.org"
MTB_EVENT_TYPE = "3148f509-b19f-11e5-907e-08002773d9e3"
YEARS = [2017, 2016]


def scrape_sas():
	mtb_events = get_mtb_events()
	# for event in mtb_events:  
	#		#Retrieve the event_reference to look up the categories
	#  	categories = get_categories(mtb_events[event][0])
	#  	time.sleep(2)
	get_categories_and_stages("/participants/event-results/pe-to-plett-mtb-2017-03-02", 46)
	#event = (db.session.query(Event.id).filter(Event.title=="PE to Plett MTB").first())
	#pprint(event.id)

def get_mtb_events(): 
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
			db_date = datetime.strptime(event_date, '%d %b %Y')
			db_event = Event(event_name, db_date)
			db_check = db.session.query(Event.title).filter(Event.title==event_name)
			if not (db.session.query(db_check.exists()).scalar()):
				db.session.add(db_event)
				db.session.flush()
				sas_event = SASEvent(db_event.id, event_reference)
				db.session.add(sas_event)
				pprint(db_event.id)
	db.session.commit()

def get_categories_and_stages(event_reference, event_id):
	categories = {}
	stages = {}
	url =  (DESTINATION_URL + event_reference)
	page = urllib.request.urlopen(url)
	soup = BeautifulSoup(page, "html.parser")
	check_stages = get_categories(soup, event_id)
	if check_stages: 
		get_event_stages(soup)

def get_categories(soup, event_id):
	category_div = soup.find('div', attrs={"id" : "category_container"})
	#Check to see if event has categories first
	if category_div:
		divs = category_div.find_all('div')
		for div in divs: 
			if div.has_attr("data-event-category-id"):
				category_reference = div["data-event-category-id"]
				category_name = div["data-loading-text"]
				category_own_stage_reference = div["data-event-stage-id"]
				#Create base category if it doesn't exist
				db_category = Category(category_name, event_id)
				db_category_check = db.session.query(Category.name).filter(Category.name==category_name)
				if not (db.session.query(db_category_check.exists()).scalar()):
					db.session.add(db_category)
					db.session.flush()
					db_sas_category = SASCategory(category_reference, category_own_stage_reference, db_category.id)
					db.session.add(db_sas_category)
					db.session.flush()
				#Handle multi-stage categories
				if (div["data-multiple-event-stages"] == "1"):
					category_multistage = True
					get_category_stages(soup, db_category.id, category_reference)
				#Handle event stages
				else: 
					category_multistage = False
	db.session.commit()			
	return category_multistage

def get_category_stages(soup, category_id, category_reference):
	stage_group_div = soup.find('div', attrs={"id" : ("ec_" + category_reference)})
	stage_divs = stage_group_div.find_all('div')
	for stage_div in stage_divs: 
		if stage_div.has_attr("data-stage-id"):
			category_stage_reference = stage_div["data-stage-id"]
			category_stage_name = stage_div["data-loading-text"]
			pprint(category_stage_name + category_stage_reference)

def get_event_stages(soup):
	pprint("do nothing")




scrape_sas()
