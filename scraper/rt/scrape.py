from bs4 import BeautifulSoup
from pprint import pprint 
from scraper.base_models.models import Event, Category, CategoryStage, EventStage, Participant, Result
from scraper.rt.rt_models import RTEvent 
from scraper.rt.rt_config import YEARS
from scraper import db
from datetime import datetime
import urllib
import json 
import time

#TODO - Add all year maps to config 
YEARS = {2017: "1500322423795", 2016: "1500322522356"}

class RT(object):

	def get_events(): 
		for year in YEARS: 
			url = "http://results.racetec.co.za/calls/call_options.ashx?cmd=get_yearevents&ds=%s" % YEARS[year]
			try: 
				page = urllib.request.urlopen(url)
				content =  page.read().decode("utf-8")
				json_content = json.loads(content)
				events = json_content["Data"]
			except (urllib.error.HTTPError):
				pass
			for event in events: 
				route_id = (event['RouteID'])
				date_string = (event['RouteDescription'][4:14])
				date = datetime.strptime(date_string, '%d/%m/%Y')
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
					#(Event.date==date) &
					(Event.title.like(("%" + description[:10] + "%")))).first()
					pprint("Venue and reference not used yet")
					pprint("%" + description[:10] + "%")
					if not db_event_result_check: 
						#Event does not exist
						pprint("Creating Event and RTEvent")
						db.session.add(db_event)
						db.session.flush()
						pprint(db_event.id)
						db_rt_event = RTEvent(db_event.id, route_id, venue)
						db.session.add(db_rt_event)
						db.session.commit()
						pprint(db_rt_event.id)
					else: 
						pprint("Creating RTEvent only")
						db_rt_event = RTEvent(db_event_result_check.id, route_id, venue)
						db.session.add(db_rt_event)
						db.session.commit()





	def get_results(route_id):
		url = "http://results.racetec.co.za/results_by_event.aspx?RID=%d" % route_id
		try: 
			page = urllib.request.urlopen(url)
			content =  page.read().decode("utf-8")
			soup = BeautifulSoup(content, "html.parser")
			#json_content = json.loads(content)
			#events = json_content["Data"]
		except (urllib.error.HTTPError):
			pass
		scripts = soup.find_all('script')
		result_string = str(scripts[2])
		json_results = json.loads((result_string[283:-53]).replace(' ', ''))
		pprint(json_results)

	pprint("Hello from RT")
	#get_events()
	#get_results(9275)