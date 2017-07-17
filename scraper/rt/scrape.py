from bs4 import BeautifulSoup
from pprint import pprint 
from scraper.base_models.models import Event, Category, CategoryStage, EventStage, Participant, Result
from scraper import db
from datetime import datetime
import urllib
import json 
import time

#TODO - Add all year maps 
YEARS = {2017: "1500322423795", 2016: "1500322522356"}

def get_events(): 
	url = "http://results.racetec.co.za/calls/call_options.ashx?cmd=get_yearevents&ds=1500321158218"
	try: 
		page = urllib.request.urlopen(url)
		content =  page.read().decode("utf-8")
		json_content = json.loads(content)
		events = json_content["Data"]
	except (urllib.error.HTTPError, urllib.error.ConnectionResetError):
		pass
	for event in events: 
		pprint(event["RouteID"])
	#pprint(json_content["Data"][1]['RouteID'])

def get_results(route_id):
	url = "http://results.racetec.co.za/results_by_event.aspx?RID=%d" % route_id
	try: 
		page = urllib.request.urlopen(url)
		content =  page.read().decode("utf-8")
		soup = BeautifulSoup(content, "html.parser")
		#json_content = json.loads(content)
		#events = json_content["Data"]
	except (urllib.error.HTTPError, urllib.error.ConnectionResetError):
		pass
	scripts = soup.find_all('script')
	result_string = str(scripts[2])
	json_results = json.loads((result_string[283:-53]).replace(' ', ''))
	pprint(json_results)

#get_events()
get_results(9275)