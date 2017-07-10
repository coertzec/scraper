from datetime import datetime, date, time
from scraper import db
from sqlalchemy.orm import relationship

class Base(db.Model):
    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime, default=datetime.utcnow())
 

class Event(Base): 
	title	= db.Column(db.String(250), unique=True)
	date 	= db.Column(db.Date)
	categories = relationship("Category")
	event_stages = relationship("EventStage")

	def __init__(self, title, date): 
		self.title = title
		self.date = date 

class Category(Base):
	name	= db.Column(db.String(250), nullable=False)
	event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
	event = db.relationship('Event', backref=db.backref('event', lazy='dynamic'))
	category_stages = relationship("CategoryStage")
	results = relationship("Result")
    
	def __init__(self,name, event_id): 
		self.name = name
		self.event_id = event_id

class CategoryStage(Base):
	name	= db.Column(db.String(250))
	category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
	category = db.relationship('Category', backref=db.backref('category', lazy='dynamic'))
	results = relationship("Result")

	def __init__(self, name, category_id): 
		self.name = name 
		self.category_id = category_id

class EventStage(Base):
	name	= db.Column(db.String(250))
	event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
	event = db.relationship('Event', backref=db.backref('event_stage_event', lazy='dynamic'))
	results = relationship("Result")

	def __init__(self, name, event_id): 
		self.name = name
		self.event_id = event_id

class Participant(Base): 
	first_name = db.Column(db.String(250))
	last_name = db.Column(db.String(250))
	sex = db.Column(db.String(1))
	birth_date = db.Column(db.Date)

	def __init__(self, first_name, last_name, sex, birth_date): 
		self.first_name = first_name
		self.last_name = last_name
		self.sex = sex
		self.birth_date = birth_date

class Result(Base): 
	position = db.Column(db.Integer)
	participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'))
	participant = db.relationship('Participant', backref=db.backref('result_category', lazy='dynamic'))
	gender_position = db.Column(db.Integer)
	time = db.Column(db.Integer)
	event_stage_id = db.Column(db.Integer, db.ForeignKey('event_stage.id'))
	event_stage = db.relationship('EventStage', backref=db.backref('result_event_stage', lazy='dynamic'))
	category_stage_id = db.Column(db.Integer, db.ForeignKey('category_stage.id'))
	category_stage = db.relationship('CategoryStage', backref=db.backref('result_category_stage', lazy='dynamic'))
	category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
	category = db.relationship('Category', backref=db.backref('result_category', lazy='dynamic'))


	def __init__(self, position, participant_id, gender_position, time, event_stage_id, category_stage_id, category_id):
		self.position = position 
		self.participant_id = participant_id
		self.gender_position = gender_position
		self.time = time 
		self.event_stage_id = event_stage_id
		self.category_stage_id = category_stage_id
		self.category_id = category_id

