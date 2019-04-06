#Import functions
import numpy as np
import datetime as dt
import sqlalchemy
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, distinct

from flask import Flask, jsonify

#Set-up database#
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#Set up Flask#
app = Flask(__name__)

#Create home page with all the routes#
@app.route("/")
def home():
    return ("Here are the available routes:</br>  "
        f"/api/v1.0/percipitation</br>"
        f"/api/v1.0/stations</br> "
        f"/api/v1.0/tobs</br>"
        f"Use date format yyyy-mm-dd</br>"
        f"/api/v1.0/&lt;start&gt;</br>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )
    
#Set up the percipitation route
@app.route("/api/v1.0/percipitation")
def percipitation():
    ##Return a list of all the percipitation for that day##
    # Query all dates
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Create a dictionary from the row data and append to the dates
    rain = []
    for date, prcp in results:
        percip_dict = {}
        percip_dict["date"] = date
        percip_dict["prcp"] = prcp
        rain.append(percip_dict)

    return jsonify(rain)

#Set up the station route
@app.route("/api/v1.0/stations")
def stations():
    ##return a list of all the stations##
    #Query stations
    results = session.query(Station.station).all()

    #Create a list
    stations = list(np.ravel(results))

    return jsonify(stations)

#Date and temperature observations from a year from the last data point
@app.route("/api/v1.0/tobs")
def tobs():
    #return a list of temperature observations(tobs) for the previous year
    #Fetch the date a year ago from the last date on the file
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    twelve_months = dt.date(f'{last_date}') - dt.timedelta(days=365)
    
    #Query list of temperatures
    temps = session.query(Measurement.tobs).\
            filter(Measurement.date == f"{twelve_months}").all()
    
    #Create a list of temperatures and jsonify
    temperatures = list(np.ravel(temps))
    return jsonify(temperatures)

#Pull temperature stats based on user entered date 
@app.route("/api/v1.0/<start>/<end>")
def temp_date_range(start, end):
    tobs_stats = session.query(Measurement.date,
                        func.min(Measurement.tobs), 
                        func.max(Measurement.tobs),
                        func.avg(Measurement.tobs)).\
                        group_by(Measurement.date).\
                        filter(Measurement.date >= start, 
                        Measurement.date < end).all()
    
    #Create a dictionary of the final temperatures 
    temperature = []
    for date, min_temp, max_temp, avg_temp in tobs_stats:
        temp_dict = {}
        temp_dict["date"] = date        
        temp_dict["min_temp"] = min_temp
        temp_dict["max_temp"] = max_temp
        temp_dict["avg_temp"] = avg_temp
        temperature.append(temp_dict)

    return jsonify(temperature)
    
#Pull temperature stats based on user entered date
@app.route("/api/v1.0/<start>")
def temp_date(start):
    #run query if only the one date is entered
    temp_date_stats = session.query(Measurement.date,
                        func.min(Measurement.tobs), 
                        func.max(Measurement.tobs),
                        func.avg(Measurement.tobs)).\
                        filter(Measurement.date == start).all()
    
    # Create a dictionary from the row data and append to the dates
    return jsonify(temp_date_stats)
    

#Define behaviour
if __name__ == '__main__':
    app.run(debug = True)