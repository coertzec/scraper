from datetime import datetime, date
from scraper import db

class Base(db.Model):
    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp)
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp, 
    				onupdate=db.func.current_timestamp)

class Event(Base): 
	__abstract__ = True 

	title	= db.Column(db.String(250), unique=True)
	date 	= db.Column(db.Date)

class Category(Base):
	__abstract__ = True

	name	= db.Column(db.String(250))

class Stage(Base):
	__abstract__ = True 

	name	= db.Column(db.String(250))