from bs4 import BeautifulSoup
from pprint import pprint 
from scraper.sas.sas_models import SASEvent, SASCategory, SASCategoryStage, SASEventStage
from scraper.base_models.models import Event, Category, CategoryStage, EventStage
from scraper import db
from datetime import datetime
import urllib
import json 
import time


#TODO - These have to go 
DESTINATION_URL = "https://www.saseeding.org"
MTB_EVENT_TYPE = "3148f509-b19f-11e5-907e-08002773d9e3"
YEARS = [2017, 2016]


def scrape_sas():
	pprint("Scraping Events")
	get_mtb_events()
	pprint("Getting categories and stages")
	for event in db.session.query(SASEvent):
		pprint("Getting Categories event:")
		pprint(event.event_id)
		get_categories_and_stages(event.event_reference, event.event_id)
		#time.sleep(2)
	pprint("Traversing event stages")
	pprint("Scrape Complete")


def get_mtb_events(): 
	for year in YEARS: 
		url = ("%s/participants/event-results/fetch-series-by-type?event_type=%s&event_year=%d" % 
			  (DESTINATION_URL, MTB_EVENT_TYPE, year))
		try: 
			page = urllib.request.urlopen(url)
			content =  page.read().decode("utf-8")
			json_content = json.loads(content)
			soup = BeautifulSoup(json_content['HTML'], "html.parser")
			anchors = soup.find_all('a')
		except urllib.error.HTTPError:
			pass
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
				db.session.commit()

def get_categories_and_stages(event_reference, event_id):
	url =  (DESTINATION_URL + event_reference)
	try: 
		page = urllib.request.urlopen(url)
	except urllib.error.HTTPError:
		return
	soup = BeautifulSoup(page, "html.parser")
	check_stages = get_categories(soup, event_id)

def get_categories(soup, event_id):
	category_div = soup.find('div', attrs={"id" : "category_container"})
	#Check to see if event has categories first
	if category_div:
		divs = category_div.find_all('div')
		for div in divs: 
			if div.has_attr("data-event-category-id"):
				#Event has categories
				category_reference = div["data-event-category-id"]
				category_name = div["data-loading-text"]
				category_own_stage_reference = div["data-event-stage-id"]
				db_category = Category(category_name, event_id)
				#Check both name and event id to allow duplicate names 
				db_category_check = db.session.query(Category.name).filter(
				(Category.name==category_name) &
				(Category.event_id==event_id))
				if not (db.session.query(db_category_check.exists()).scalar()):
					db.session.add(db_category)
					db.session.flush()
					db_sas_category = SASCategory(category_reference, category_own_stage_reference, db_category.id)
					db.session.add(db_sas_category)
					db.session.flush()
					db.session.commit()			
					if (div["data-multiple-event-stages"] == "1"):
						#Event has stages with their own categories
						get_category_stages(soup, db_category.id, category_reference)
	else:
		#Event does not have categories
		get_event_stages(soup, event_id)


def get_category_stages(soup, category_id, category_reference):
	stage_group_div = soup.find('div', attrs={"id" : ("ec_" + category_reference)})
	stage_divs = stage_group_div.find_all('div')
	for stage_div in stage_divs: 
		if stage_div.has_attr("data-stage-id"):
			category_stage_reference = stage_div["data-stage-id"]
			category_stage_name = stage_div["data-loading-text"]
			db_category_stage = CategoryStage(category_stage_name, category_id)
			#Check both name and category id to allow duplicate names 
			db_category_stage_check = db.session.query(CategoryStage.name).filter(
				(CategoryStage.name==category_stage_name) &
				(CategoryStage.category_id==category_id))
			if not (db.session.query(db_category_stage_check.exists()).scalar()):
				db.session.add(db_category_stage)
				db.session.flush()
				db_sas_category_stage = SASCategoryStage(db_category_stage.id, category_stage_reference)
				db.session.add(db_sas_category_stage)
				db.session.flush()
				db.session.commit()

def get_event_stages(soup, event_id):
	all_event_stage_divs = soup.find('div', class_ = "row categories_stages event-sub-types")
	#Check if event has stages
	if all_event_stage_divs:
		event_stage_divs = all_event_stage_divs.find_all ('div')
		for event_stage_div in event_stage_divs: 
			if event_stage_div.has_attr("data-stage-id"):
				#Event has stages and no categories
				event_stage_reference = event_stage_div["data-stage-id"]
				event_stage_name = event_stage_div["data-loading-text"]
				db_event_stage = EventStage(event_stage_name, event_id)
				#Check if it exists by name and ID and add if it doesn't
				db_event_stage_check = db.session.query(EventStage.name).filter(
					(EventStage.name==event_stage_name) &
					(EventStage.event_id==event_id))
				if not (db.session.query(db_event_stage_check.exists()).scalar()):
					db.session.add(db_event_stage)
					db.session.flush()
					db_sas_event_stage = SASEventStage(db_event_stage.id, event_stage_reference)
					db.session.add(db_sas_event_stage)
					db.session.flush()
					db.session.commit()
	else: 
		#Event has no stages or categories
		#create new stage for just the overall results, unless event has no results
		event_stage_reference_div = soup.find('div', class_ = "result-row load-results")
		if event_stage_reference_div:
			if event_stage_reference_div.has_attr("data-stage"):
				event_stage_reference = event_stage_reference_div["data-stage"]
				sas_event = db.session.query(SASEvent).filter(SASEvent.event_id==event_id).first()
				db_event_stage_check = db.session.query(EventStage.name).filter(
					(EventStage.name=="Overall Results") &
					(EventStage.event_id==sas_event.event_id))
				if not (db.session.query(db_event_stage_check.exists()).scalar()):
					db_event_stage = EventStage("Overall Results", sas_event.event_id)
					db.session.add(db_event_stage)
					db.session.flush()
					db_sas_event_stage = SASEventStage(db_event_stage.id, event_stage_reference)
					db.session.add(db_sas_event_stage)
					db.session.commit()


scrape_sas()
