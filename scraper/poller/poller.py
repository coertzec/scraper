from scraper.rt import scrape as rt_scraper
from scraper.sas import scrape as sas_scraper

class Poller(object): 

	def poll(self):
		try:
			rt_scraper.scrape_rt()
		except urllib.error.URLError:
			print("Could not connect to SAS")
		try: 
			sas_scraper.scrape_sas()
		except urllib.error.URLError:
			print ("Could not connect to RT})
