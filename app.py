# imports
# region
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# endregion

# initial setup of database and engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)
conn = engine.connect()

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# %%
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB

# %%
# Flask setup
app = Flask(__name__)


# routes
@app.route('/')
def hello():
    """List all available apis"""

    return (
        f'Available Routes:<br/>'
        f'/api/v1.0/Precipitation<br/>'
        f'/api/v1.0/Stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/<start><br/>'
        f'/api/v1.0/<start>/<end><br/>'
    )


@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(bind=engine)

    # finds the last (most recent) date in the data
    last_date = session.query(
        Measurement.date
    ).order_by(
        Measurement.date.desc()
    ).first()[0]

    # convert to date
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')

    # get data going back 1 year from last_date
    last_year = last_date - dt.timedelta(days=365)

    precip = session.query(
        Measurement.date, Measurement.prcp
    ).filter(
        Measurement.date > last_year
    ).order_by(
        Measurement.date
    ).all()

    session.close()
    # convert query output to dict where {date: prcp}
    # return the dict as a json
    precip_dict = jsonify(dict(precip))

    return precip_dict


@app.route('/api/v1.0/Stations')
def stations():
    session = Session(bind=engine)

    all_stations = session.query(
        Measurement.station, Measurement.date, Measurement.prcp, Measurement.tobs
    ).order_by(Measurement.station).all()

    session.close()

    # convert tuple to list
    all_stations = [i for tup in all_stations for i in tup]

    return jsonify(all_stations)


@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(bind=engine)

    # finds the last (most recent) date in the data
    last_date = session.query(
        Measurement.date
    ).order_by(
        Measurement.date.desc()
    ).first()[0]

    # convert to date
    last_year = dt.datetime.strptime(
        last_date, '%Y-%m-%d'
    ) - dt.timedelta(days=365)

    most_active_station = engine.execute(
        'SELECT station '
        'FROM (SELECT station, COUNT(station) '
        'AS mycount'
        '       FROM measurement GROUP BY station ORDER BY mycount DESC) '
        'measurement').first()[0]

    temps = session.query(
        Measurement.date, Measurement.tobs, Measurement.prcp
    ).filter(
        Measurement.date > last_year,
        Measurement.station == most_active_station
    ).order_by(
        Measurement.date
    ).all()

    session.close()

    dict = {}
    return_list =[]

    for date, tobs, rain in temps:
        dict['date'] = date
        dict['tobs'] = tobs
        dict['rain'] = rain

        return_list.append(dict)

    return jsonify(return_list)



if __name__ == '__main__':
    app.run(debug=True)
