# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, inspect, func, and_
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# 1. Start at the homepage.
#    List all the available routes.
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Alchemy Challenge APP API!<br/>"
        f"Available Routes for Hawaii Weather Data Aug 23, 2016 - Aug 23, 2017:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Active Weather stations: /api/v1.0/stations<br/>"
        f"Daily observations for Station USC00519281: /api/v1.0/tobs<br/>"
        f"Weater Stats for Start Date to 2017-08-23 (Default Date): /api/v1.0/yyyy-mm-dd<br/>"
        f"Weater Stats for Date Range: /api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"
        f"/api/v1.0/<end><br/>"
    )

# 2. Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary 
#          using date as the key and prcp as the value.
#    Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Percipitation data"""
    start_date = '2016-08-23'
    scores = session.query(Measurement.date, func.avg(Measurement.prcp)).\
        filter(Measurement.date > start_date). \
        group_by(Measurement.date).all()
     
    session.close()

    # Convert the list to a Dictionary
    precipitation_dict = []
    for date, prcp in scores:
        dict_prcp ={}
        dict_prcp["date"] = date
        dict_prcp["prcp"] = prcp
        precipitation_dict.append(dict_prcp)

    return jsonify(precipitation_dict)

# 3. Return a JSON list of stations from the dataset.
# 
@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)   

    """Return a list of all Station data"""
    active_stations = session.query(Station.name, Measurement.station, func.count(Measurement.station)).\
        join(Station, Measurement.station==Station.station).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    session.close()   
 
       # Convert list of tuples into normal list
    all_stations = list(np.ravel(active_stations))
    return jsonify(all_stations)

 # 4. /api/v1.0/tobs Query the dates and temperature observations of the most-active station for the previous year of data.
#    Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)   

    """Query the dates and temperature observations of the most-active station"""
    act_station = 'USC00519281'
    start_date = '2016-08-23'
    station_tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > start_date, Measurement.station == act_station). \
        group_by(Measurement.date).all()
     
    session.close()
     # Convert the list to a Dictionary
    observation_dict = []
    for date, tobs in station_tobs:
        dict_tobs ={}
        dict_tobs["date"] = date
        dict_tobs["tobs"] = tobs
        observation_dict.append(dict_tobs)

    return jsonify(observation_dict)

# 5. /api/v1.0/<start> and /api/v1.0/<start>/<end>
#    Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#    For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
#    For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>")
def sel_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)   

    """Query the dates and temperature observations of the stations"""
   
    date_start=session.query(Measurement.station, Station.name,
              func.min(Measurement.tobs), 
              func.max(Measurement.tobs),
              func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        join(Station, Measurement.station==Station.station).\
        group_by(Measurement.station).all()
     
    session.close()
     # Convert the list to a Dictionary
    statistics_start_dict = []
    for station, name, min, max, avg in date_start:
        dict_stat ={}
        dict_stat["Station"] = station
        dict_stat["Station_Name"] = name
        dict_stat["Min"] = min
        dict_stat["Max"] = max
        dict_stat["Average"] = avg
        statistics_start_dict.append(dict_stat)
    if len(statistics_start_dict) > 0  :
        return jsonify(statistics_start_dict)
    else: 
        return jsonify({"error": f'Dates not found, invalid range or invalid date format'}), 404
@app.route("/api/v1.0/<start>/<stop>")
def sel_dates(start, stop):
    # Create our session (link) from Python to the DB
    session = Session(engine)   

    """Query the dates and temperature observations of the stations"""
   
    date_start_stop=session.query(Measurement.station, Station.name,
              func.min(Measurement.tobs), 
              func.max(Measurement.tobs),
              func.avg(Measurement.tobs)).\
        filter(and_(Measurement.date <= stop,  Measurement.date >= start)).\
        join(Station, Measurement.station==Station.station).\
        group_by(Measurement.station).all()
     
    session.close()
     # Convert the list to a Dictionary
    statistics_start_stop_dict = []
    for station, name, min, max, avg in date_start_stop:
        dict_stop ={}
        dict_stop["Station"] = station
        dict_stop["Station_Name"] = name
        dict_stop["Min"] = min
        dict_stop["Max"] = max
        dict_stop["Average"] = avg
        statistics_start_stop_dict.append(dict_stop)
    if len(statistics_start_stop_dict) > 0  :
        return jsonify(statistics_start_stop_dict)
    else: 
        return jsonify({"error": f'Dates not found, invalid range or invalid date format'}), 404
# run the app
if __name__ == '__main__':
    app.run(debug=True)
   