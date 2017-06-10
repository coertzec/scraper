from flask import Flask
from flask_sqlalchemy import SQLAlchemy

scraper = Flask(__name__)

# Configurations
scraper.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(scraper)

from scraper.sas import scrape as sas_scraper
from scraper.base_models import models


# Build the database:
# This will create the database file using SQLAlchemy
db.create_all()