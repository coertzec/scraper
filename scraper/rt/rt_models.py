from scraper.base_models.models import Base
from datetime import datetime, date
from scraper import db

class RTEvent(Base):
	event_reference	= db.Column(db.String(250), unique=True)
	venue = db.Column(db.String(250))
	event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
	event = db.relationship('Event', backref=db.backref('rt_to_event', lazy='dynamic'))
    
	def __init__(self, event_id, event_reference, venue): 
		self.event_id = event_id
		self.event_reference = event_reference
		self.venue = venue