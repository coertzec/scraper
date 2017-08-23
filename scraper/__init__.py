from flask import Flask
from flask_sqlalchemy import SQLAlchemy

scraper = Flask(__name__)
scraper.config.from_object('config')
db = SQLAlchemy(scraper)

from scraper.base_models import models as models
from scraper.sas import sas_models as sas_models
from scraper.rt import rt_models as rt_models
# Build the database
db.create_all()

from scraper.poller.poller import Poller
poller = Poller()
poller.poll()





