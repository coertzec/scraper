from datetime import datetime, date
from scraper import db

class Base(db.Model):
    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime, default=datetime.utcnow())
 

class Event(Base): 
	title	= db.Column(db.String(250), unique=True)
	date 	= db.Column(db.Date)

	def __init__(self, title, date): 
		self.title = title
		self.date = date 

class Category(Base):
	name	= db.Column(db.String(250), nullable=False)
	event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
	event = db.relationship('Event', backref=db.backref('event', lazy='dynamic'))
    
	def __init__(self,name, event_id): 
		self.name = name
		self.event_id = event_id

class CategoryStage(Base):
	name	= db.Column(db.String(250))
	category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
	category = db.relationship('Category', backref=db.backref('category', lazy='dynamic'))

	def __init__(self, name, category_id): 
		self.name = name 
		self.category_id = category_id

class EventStage(Base):
	name	= db.Column(db.String(250))
	event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
	event = db.relationship('Event', backref=db.backref('event_stage_event', lazy='dynamic'))

	def __init__(self, name, event_id): 
		self.name = name
		self.event_id = event_id
