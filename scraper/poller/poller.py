from scraper.rt import scrape as rt_scraper
from scraper.sas import scrape as sas_scraper

class Poller(object): 

	def poll(self):
		rt_scraper.scrape_rt()
		sas_scraper.scrape_sas()