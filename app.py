# Import the dependencies.
import numpy as np
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
Measurements = Base.classes.measurement
Stations = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
#define home route
@app.route('/')
def home():
    """List all Available api routes."""
    return (
        f"Welcome to Michael Dong Woo Kang's Climate App API!<br/><br/>"
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-08-23<br/>"
        f"/api/v1.0/2016-08-23/2017-08-23"
    )

#define precipitation route
@app.route('/api/v1.0/precipitation')
def precipitation():
    """Return the JSON representation of your dictionary."""
    # Calculate the date one year ago from the last date in the database.
    most_recent_date = session.query(func.max(Measurements.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months.
    results = session.query(Measurements.date, Measurements.prcp).filter(Measurements.date >= one_year_ago).all()

    # Convert the query results to a dictionary.
    precipitation_data = {date: prcp for date, prcp in results}
    session.close()
    #return jsonified
    return jsonify(precipitation_data)

#define the stations route
@app.route('/api/v1.0/stations')
def stations():
    """Return a JSON list of stations from the dataset."""
    # Query all stations.
    results = session.query(Stations.station).all()

    # Convert the query results to a list.
    stations_list = [station for station, in results]
    session.close()
    #return jsonified
    return jsonify(stations_list)

#define the temperature observations
@app.route('/api/v1.0/tobs')
def tobs():
    # Calculate the date one year ago from the last date in the database.
    most_recent_date = session.query(func.max(Measurements.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Find the most active station.
    most_active_station = session.query(Measurements.station, func.count(Measurements.station)).\
        group_by(Measurements.station).\
        order_by(func.count(Measurements.station).desc()).first()[0]

    # Query temperature observations for the last 12 months from the most active station.
    results = session.query(Measurements.date, Measurements.tobs).\
        filter(Measurements.station == most_active_station).\
        filter(Measurements.date >= one_year_ago).all()

    # Convert the query results to a list of dictionaries.
    tobs_list = [{'Date': date, 'Temperature': tobs} for date, tobs in results]
    session.close()
    #return jsonified
    return jsonify(tobs_list)

#define start and end date route
@app.route('/api/v1.0/<start_date>')
@app.route('/api/v1.0/<start_date>/<end_date>')
def start_end_date(start_date = None, end_date = None):
    #define start_date and end_date
    start_date = dt.datetime.strptime(start_date,'%Y-%m-%d')
    # Query TMIN, TAVG, and TMAX for dates between the start and end date.
   # if conditional
    if not end_date:
        results = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)). \
            filter(Measurements.date >= start_date).all()
        session.close()
        summary_dict = list(np.ravel(results))
        # return jsonified
        return jsonify(summary_dict)
    end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')
    results = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        filter(Measurements.date >= start_date).filter(Measurements.date <= end_date).all()
    # Convert the query results to a dictionary.
    summary_dict = list(np.ravel(results))
    session.close()
    #return jsonified
    return jsonify(summary_dict)

# Run the Flask app.
if __name__ == '__main__':
    app.run(debug=True)

