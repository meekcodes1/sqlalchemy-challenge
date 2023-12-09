# Import the dependencies.
import numpy as np
import os
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import pandas as pd

from flask import Flask, jsonify


#################################################
# Database Setup (Had to use os library due to error)
#################################################
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the database file
database_path = os.path.join(script_dir, "Resources", "hawaii.sqlite")

# Create the engine with the absolute path
engine = create_engine(f"sqlite:///{database_path}")


# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"   
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/*start_date*<br/>"
        f"/api/v1.0/*start_date*/*end_date*"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    # Calculate the date one year from the last date in data set.
    recent_date_minus_1 = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    year_data = session.query(measurement.date, measurement.prcp).filter(measurement.date > recent_date_minus_1)

    # Save the query results as a Pandas DataFrame. Explicitly set the column names
    year_data_df = pd.DataFrame(year_data, columns=["date", "precipitation"])

    # Sort the dataframe by date
    year_data_df = year_data_df.sort_values(by='date', ascending=True)

    # Drop NA and convert to dictionary for JSON
    prec_dict = year_data_df.dropna().to_dict()
    
    return jsonify(prec_dict)

@app.route("/api/v1.0/stations")
def stations():

    # Return JSON list of stations
    station = Base.classes.station
    stations = session.query(station)
    station_list = []

    for station in stations:
        station_list.append(station.station)

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():

    # dates and temperature observations of the most-active station for the previous year of data
    recent_date_minus_1 = dt.date(2017,8,23) - dt.timedelta(days=365)
    active_temp = session.query(measurement.tobs, measurement.date).filter(measurement.station == "USC00519281")
    twelve_mo_temp = active_temp.filter(measurement.date > recent_date_minus_1)
    twelve_mo_temp_df = pd.DataFrame((twelve_mo_temp))

    # Drop NA and convert to dictionary for JSON
    twelve_dict = twelve_mo_temp_df.dropna().to_dict()
    
    return jsonify(twelve_dict)

@app.route("/api/v1.0/<start>")
def start(start):

    measurement = Base.classes.measurement

    # generates metrics after the "start" date
    start_date_min = session.query(func.min(measurement.tobs)).filter(measurement.date >= start).first()
    start_date_max = session.query(func.max(measurement.tobs)).filter(measurement.date >= start).first()
    start_date_avg = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start).first()

    combined = {"MIN": start_date_min[0], "MAX": start_date_max[0], "AVG": start_date_avg[0]}

    return jsonify(combined)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    
    measurement = Base.classes.measurement

    # generates metrics after the "start" date, before the "end" date
    start_date_min = session.query(func.min(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).first()
    start_date_max = session.query(func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).first()
    start_date_avg = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).first()

    combined = {"MIN": start_date_min[0], "MAX": start_date_max[0], "AVG": start_date_avg[0]}

    return jsonify(combined)

if __name__ == '__main__':
    app.run(debug=True)
