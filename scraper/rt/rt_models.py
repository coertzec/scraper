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

class RTCategory(Base):
	category_reference = db.Column(db.String(250), unique=True)
	category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
	category = db.relationship('Category', backref=db.backref('rt_to_category', lazy='dynamic'))

	def __init__(self, category_reference, category_id): 
		self.category_reference = category_reference
		self.category_id = category_id

class RTEventStage(Base):
	stage_reference = db.Column(db.String(250), unique=True)
	event_stage_id = db.Column(db.Integer, db.ForeignKey('event_stage.id'))
	event_stage = db.relationship('EventStage', backref=db.backref('rt_event_stage', lazy='dynamic'))
	
	def __init__(self, event_stage_id, stage_reference): 
		self.event_stage_id = event_stage_id
		self.stage_reference = stage_reference