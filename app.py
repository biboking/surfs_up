import datetime as dt
import numpy as np
import pandas as p

# the dependencies we need for SQLAlchemy, which will help us access our data in the SQLite database
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# import flask
from flask import Flask, jsonify

# Set Up the Database

#Access and query our SQLite database file.
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect the database into our classes
Base = automap_base()
Base.prepare(engine, reflect=True)

#save our references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# create a session link from Python to our database
session = Session(engine)

# Set Up Flask
app = Flask(__name__)

# define the welcome route
@app.route("/")
def welcome():  ##create a function
    return(
    '''
    Welcome to the Climate Analysis API! 
    Available Routes: 
    /api/v1.0/precipitation 
    /api/v1.0/stations 
    /api/v1.0/tobs 
    /api/v1.0/temp/start/end 
    ''')
# New route for precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)  #calculates the date one year ago from the most recent date
    precipitation = session.query(Measurement.date, Measurement.prcp).\
      filter(Measurement.date >= prev_year).all()   #get the date and precipitation for the previous year
    precip = {date: prcp for date, prcp in precipitation}
    return   jsonify(precip)  # use jsonify() to format our results into a JSON structured file


# New route for stations
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results)) # use np.ravel() to unraveling our results into a one-dimensional array, then convert our unraveled results into a list
    return jsonify(stations=stations) #to return our list as JSON, we need to add stations=stations to format our list into JSON

# Monthly Temperature Route
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
      filter(Measurement.station == 'USC00519281').\
      filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

# The route for the minimum, maximum, and average temperatures
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps=temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)