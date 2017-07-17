from flask import Flask
from flask_sqlalchemy import SQLAlchemy

scraper = Flask(__name__)

# Configurations
scraper.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(scraper)


from scraper.base_models import models as models
from scraper.sas import sas_models as sas_models
# Build the database
db.create_all()

from scraper.sas import scrape as sas_scraper
from scraper.rt import scrape as rt_scraper





