from angular_flask import app

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager
from flask.ext.pymongo import PyMongo

app.config['MONGO_DBNAME'] = 'fplffc'
app.config['MONGO_URI'] = 'mongodb://bendknee:jonarys@ds161164.mlab.com:61164/fplffc' 

mongo = PyMongo(app)
db = SQLAlchemy(app)

api_manager = APIManager(app, flask_sqlalchemy_db=db)
