from bs4 import BeautifulSoup
from pprint import pprint 
from scraper.sas.sas_models import SASEvent, SASCategory, SASCategoryStage, SASEventStage
from scraper.base_models.models import Event, Category, CategoryStage, EventStage, Participant, Result
from scraper.sas.sas_config import DESTINATION_URL, MTB_EVENT_TYPE, YEARS
from scraper import db
from datetime import datetime
import urllib
import json 
import time

def scrape_sas():
	pprint("Scraping Events")
	get_mtb_events()
	pprint("Getting categories and stages")
	for event in db.session.query(SASEvent):
		pprint(event.event_id)
		get_categories_and_stages(event.event_reference, event.event_id)
		#time.sleep(2)
	for event_stage in db.session.query(SASEventStage):
		pprint("Getting event stage results")
		base_event_stage = db.session.query(EventStage).filter(EventStage.id==event_stage.event_stage_id).first()
		if (base_event_stage.results):
			pprint("Event has results")
		else:
			write_stage_results(event_stage.stage_reference, event_stage.event_stage_id, "event")
	for category_stage in db.session.query(SASCategoryStage):
		pprint("Getting category stage results")
		base_category_stage = db.session.query(CategoryStage).filter(CategoryStage.id==category_stage.category_stage_id).first()
		if (base_category_stage.results):
			pprint("Category stage has results")
		else: 
			write_stage_results(category_stage.stage_reference, category_stage.category_stage_id, "category")
	for category in db.session.query(SASCategory):
		pprint("Getting category results")
		base_category = db.session.query(Category).filter(Category.id==category.category_id).first()
		if (base_category.results):
			pprint("Category has results")
		else: 
			if (not base_category.category_stages):
				write_category_results(category.stage_reference, category.id)
			else:
				pprint("No results but has category stages")
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
		except (urllib.error.HTTPError, urllib.error.ConnectionResetError):
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
	event = db.session.query(Event).filter(Event.id==event_id).first()
	if (event.categories or event.event_stages):
		pprint("Event Exists")
	else: 
		url =  (DESTINATION_URL + event_reference)
		try: 
			page = urllib.request.urlopen(url)
		except (urllib.error.HTTPError, urllib.error.URLError):
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
				#Check SAS category for duplicates as well 
				db_sas_category_check = db.session.query(SASCategory).filter(
				(SASCategory.category_reference==category_reference) &
				(SASCategory.stage_reference==category_own_stage_reference))
				if not (db.session.query(db_category_check.exists()).scalar()):
					db.session.add(db_category)
					db.session.flush()
					if not (db.session.query(db_sas_category_check.exists()).scalar()):
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

def get_results(event_reference): 
	url = ("%s/participants/event-results/add-results?stage_id=%s&from=0&count=9999" % 
			  (DESTINATION_URL, event_reference))
	pprint(url)
	try: 
		page = urllib.request.urlopen(url)
	except (urllib.error.HTTPError, urllib.error.ConnectionResetError):
		return
	content =  page.read().decode("utf-8")
	json_content = json.loads(content)
	json_results = json_content['rows']
	return json_results

def write_stage_results(stage_reference, stage_id, stage_type):
	results = get_results(stage_reference)
	category_stage_id = None
	event_stage_id = None
	if (stage_type=="event"):
		event_stage_id = stage_id
	elif (stage_type=="category"):
		category_stage_id = stage_id
	if results:
		for result in results: 
			participant_id = get_participant(result)
			db_result_check = db.session.query(Result).filter(
				(Result.position==result['overall_pos']) &
				(Result.gender_position==result['gender_pos']) & 
				(Result.time==result['time_taken_seconds']) & 
				(Result.event_stage_id==event_stage_id) &
				(Result.category_stage_id==category_stage_id))
			if not (db.session.query(db_result_check.exists()).scalar()):
				if (stage_type=="category"): 
					db_result = Result(result['overall_pos'], participant_id, result['gender_pos'],
					result['time_taken_seconds'], None, category_stage_id, None)
				elif (stage_type=="event"):
					db_result = Result(result['overall_pos'], participant_id, result['gender_pos'],
				    result['time_taken_seconds'], event_stage_id, None, None)
				db.session.add(db_result)
				db.session.commit()

def write_category_results(category_reference, category_id):
	results = get_results(category_reference)
	for result in results: 
		participant_id = get_participant(result)

		db_result_check = db.session.query(Result).filter(
			(Result.position==result['overall_pos']) &
			(Result.gender_position==result['gender_pos']) & 
			(Result.time==result['time_taken_seconds']) & 
			(Result.category_id==category_id)).first()
		if not db_result_check:
			db_category_result = Result(result['overall_pos'], participant_id,
			result['gender_pos'], result['time_taken_seconds'], None, None, category_id)
			db.session.add(db_category_result)
			db.session.commit()

def get_participant(result):
	if result['date_of_birth']:
		birth_date = datetime.strptime(result['date_of_birth'], '%Y-%m-%d').date()
	else:
		birth_date = None
	db_participant_check = db.session.query(Participant).filter(
		(Participant.first_name==result['first_name']) &
		(Participant.last_name==result['last_name']) & 
		(Participant.sex==result['person_sex']) & 
		(Participant.birth_date==birth_date))
	if not (db.session.query(db_participant_check.exists()).scalar()):
		db_participant = Participant(result['first_name'], result['last_name'],
		result['person_sex'], birth_date)
		db.session.add(db_participant)
		db.session.commit()
		return db_participant.id
	else: 
		return db_participant_check.first().id



