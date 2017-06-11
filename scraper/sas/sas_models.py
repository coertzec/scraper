from scraper.base_models.models import Base
from datetime import datetime, date
from scraper import db

class SASEvent(Base):
	event_reference	= db.Column(db.String(250), unique=True)
	event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
	event = db.relationship('Event', backref=db.backref('event', lazy='dynamic'))
    
	def __init__(self, event_id, event_reference): 
		self.event_id = event_id
		self.event_reference = event_reference


class SASCategory(Base):
	category_reference = db.Column(db.String(250), unique=True)
	stage_reference = db.Column(db.String(250), unique=True)
	category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
	category = db.relationship('Category', backref=db.backref('category', lazy='dynamic'))

	def __init__(self, category_reference, stage_reference, category_id): 
		self.category_reference = category_reference
		self.stage_reference = stage_reference
		self.category_id = category_id

class SASEventStage(Base):
	stage_reference = db.Column(db.String(250), unique=True)
	

class SASCategoryStage(Base):
	stage_reference = db.Column(db.String(250), unique=True)
	# category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
	# category = db.relationship('Category', backref=db.backref('posts', lazy='dynamic'))

	# def __init__(self, category_id, stage_reference): 
	# 	self.category_id = category_id
	# 	self.stage_reference = stage_reference