from bs4 import BeautifulSoup
from pprint import pprint 
from scraper.base_models.models import Event, Category, CategoryStage, EventStage, Participant, Result
from scraper.rt.rt_models import RTEvent, RTEventStage, RTCategory
from scraper.rt.rt_config import YEARS, DESTINATION_URL
from scraper import db
from datetime import datetime, timedelta
import urllib
import json 
import time

STAGE = "stage"
CATEGORY = "category"

def scrape_rt():
	get_events_categories_stages()
	for event_stage in db.session.query(RTEventStage):
		base_event_stage = db.session.query(EventStage).filter(EventStage.id==event_stage.event_stage_id).first()
		if (base_event_stage.results):
			pprint("Stage already has results")
		else:
			get_results(int(float(event_stage.stage_reference)), STAGE)
	for category in db.session.query(RTCategory):
		base_category = db.session.query(Category).filter(Category.id==category.category_id).first()
		if (base_category.results): 
			pprint("Category already has results")
		else:
			get_results(int(float(category.category_reference)), CATEGORY)


def get_events_categories_stages(): 
	for year in YEARS: 
		url = "%s/calls/call_options.ashx?cmd=get_yearevents" % (DESTINATION_URL)
		form_data = {'year': year}
		params = urllib.parse.urlencode(form_data)
		binary_data = params.encode('UTF-8')
		try: 
			page = urllib.request.urlopen(url, binary_data)
			content =  page.read().decode("utf-8")
			json_content = json.loads(content)
			events = json_content["Data"]
		except (urllib.error.HTTPError):
			pass
		for event in events: 
			route_id = (event['RouteID'])
			date_string = (event['RouteDescription'][4:14])
			date = datetime.strptime(date_string, '%d/%m/%Y').date()
			description = (event['RouteDescription'][15:])
			venue = (event['StartVenue'])
			db_event = Event(description, date)

			#Check if RT event exists 
			db_rt_event_result_check = db.session.query(RTEvent).filter(
			(RTEvent.venue==venue) &
			(RTEvent.event_reference==route_id)).first()
			if not db_rt_event_result_check:
				#RT event does not exist, check if event exists
				db_event_result_check = db.session.query(Event).filter(
				(Event.date==date) &
				(Event.title.like(description[:15] + "%"))).first()
				if not db_event_result_check: 
					#Event does not exist
					pprint("Creating Event and RTEvent and Category")
					db.session.add(db_event)
					db.session.flush()
					db_rt_event = RTEvent(db_event.id, route_id, venue)
					db.session.add(db_rt_event)
					db_category = Category(description[-7:], db_rt_event.id)
					db.session.add(db_category)
					db.session.flush()
					db_rt_category = RTCategory(route_id, db_category.id)
					db.session.add(db_rt_category)
					db.session.commit()
				else: 
					#Check if it is a stage
					if ((description.find('Stage')) != (-1)):
						stage_name = (description[(description.index('Stage')):])
						db_stage_result_check = db.session.query(EventStage).filter(
						(EventStage.name==stage_name) &
						(EventStage.event_id==db_event_result_check.id)).first()
						if not db_stage_result_check:
							print("Creating stage")
							db_stage = EventStage(stage_name, db_event_result_check.id)
							db.session.add(db_stage)
							db.session.flush()
							db_rt_stage = RTEventStage(db_stage.id, route_id)
							db.session.add(db_rt_stage)
							db.session.commit()
					else: 
					#It is a Category
						db_category_result_check = db.session.query(Category).filter(
						(Category.name==description[-7:]) &
						(Category.event_id==db_event_result_check.id)).first()
						if not db_category_result_check:
							pprint("Creating Category")
							db_category = Category(description[-7:], db_event_result_check.id)
							db.session.add(db_category)
							db.session.flush()
							db_rt_category = RTCategory(route_id, db_category.id)
							db.session.add(db_rt_category)
							db.session.commit()
		
def duration_to_sec(duration):
	split_values = duration.split(":")
	seconds = ((int(float(split_values[2]))) + (int(float(split_values[1])) * 60) + (int(float(split_values[0])) * 3600))
	return seconds

def get_results(route_id, type):
	print("get_results")
	url = "%s/results_by_event.aspx?RID=%d" % (DESTINATION_URL, route_id)
	try: 
		page = urllib.request.urlopen(url)
		content =  page.read().decode("utf-8")
		soup = BeautifulSoup(content, "html.parser")
	except (urllib.error.HTTPError):
		pass
	scripts = soup.find_all('script')
	result_string = str(scripts[2])
	try:
		#optimistic
		json_results = json.loads((result_string[283:-53]).replace(' ', ''))
	except json.decoder.JSONDecodeError:
		try: 
			#bracket cut off
			json_results = json.loads((result_string[283:-53]).replace(' ', '') + "]")
		except json.decoder.JSONDecodeError:
			try:
				#extra characters
				json_string = result_string[283:-53].replace(' ', '')
				json_results = json.loads(json_string.split(']')[0] + "]")	
			except json.decoder.JSONDecodeError:
				try: 
					#short string (worst case)
					json_string = result_string[283:-53].replace(' ', '')
					bracket_index = json_string.rfind("{", 0, len(json_string))
					json_results = json.loads(json_string[:bracket_index][:-1] + "]")
				except json.decoder.JSONDecodeError:
					print(json_string)
	for result in json_results: 
		participant_id = get_participant(result)
		gender_position_string = result['GenderPos']
		gender_position = gender_position_string.split('/')[0]
		time_string = result['RaceTime']
		seconds = duration_to_sec(time_string)
		if (type == CATEGORY):
			rt_category = db.session.query(RTCategory).filter(RTCategory.category_reference==route_id).first()
			category_id = rt_category.category_id
			db_result_check = db.session.query(Result).filter(
				(Result.position==result['Position']) &
				(Result.gender_position==gender_position) & 
				(Result.time==seconds) & 
				(Result.category_id==category_id)).first()
			if not db_result_check:
				db_category_result = Result(result['Position'], participant_id,
				gender_position, seconds, None, None, category_id)
				db.session.add(db_category_result)
				db.session.commit()
		if (type == STAGE):
			rt_event_stage = db.session.query(RTEventStage).filter(RTEventStage.stage_reference==route_id).first()
			stage_id = rt_event_stage.event_stage_id
			db_result_check = db.session.query(Result).filter(
				(Result.position==result['Position']) &
				(Result.gender_position==gender_position) & 
				(Result.time==seconds) & 
				(Result.event_stage_id==stage_id)).first()
			if not db_result_check:
				db_result = Result(result['Position'], participant_id, gender_position,
				seconds, stage_id, None, None)
				db.session.add(db_result)
				db.session.commit()

def get_participant(result): 
	name = (result['NameAndTeam']).split(',')
	if (len(name) > 1):
		last_name = name[0]
		first_name = name[1]
	else:
		return 0
	rider_id = result["RiderID"]
	gender = result["Gender"]
	db_participant_check = db.session.query(Participant).filter(
		(Participant.first_name==first_name) &
		(Participant.last_name==last_name) & 
		(Participant.sex==gender) & 
		(Participant.birth_date==None)).first()
	if not db_participant_check:
		db_participant = Participant(first_name, last_name,
		gender, None)
		db.session.add(db_participant)
		db.session.commit()
		return db_participant.id
	else: 
		return db_participant_check.id

