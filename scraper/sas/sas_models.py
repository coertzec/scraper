from scraper.base_models.models import Event, Category, Stage
from datetime import datetime, date
from scraper import db

class SASEvent(Event):
	event_reference	= db.Column(db.String(250), unique=True)
