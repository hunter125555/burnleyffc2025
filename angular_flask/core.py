import os
from dotenv import load_dotenv

from angular_flask import app

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager
from flask.ext.pymongo import PyMongo

APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

app.config['MONGO_DBNAME'] = os.getenv('DATABASE_NAME')
app.config['MONGO_URI'] = os.getenv('DATABASE_URI')

mongo = PyMongo(app)
db = SQLAlchemy(app)

api_manager = APIManager(app, flask_sqlalchemy_db=db)