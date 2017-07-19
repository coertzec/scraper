from scraper.sas.scrape import SAS as SAS
from scraper.rt.scrape import RT as RT

class Poller(object): 
	sas = SAS()
	rt = RT()