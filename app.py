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

Session = sqlalchemy.orm.sessionmaker(engine)
# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB

# Flask setup
app = Flask(__name__)

# routes
@app.route('/')
def hello():
    """List all available apis"""

    return (
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/<start><br/>'
        f'/api/v1.0/<start>/<end><br/>'
    )


@app.route('/api/v1.0/precipitation')
def precipitation():
    with Session() as session:
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
    with Session() as session:
        precip = session.query(
            Measurement.date, Measurement.prcp
        ).filter(
            Measurement.date > last_year
        ).order_by(
            Measurement.date
        ).all()

    # convert query output to dict where {date: prcp}
    # return the dict as a json
    precip_dict = dict(precip)

    return jsonify(precip_dict)


@app.route('/api/v1.0/stations')
def stations():
    # Session = sqlalchemy.orm.sessionmaker(engine)

    with Session() as session:
        all_stations = session.query(
            Measurement.station, Measurement.date, Measurement.prcp, Measurement.tobs
        ).order_by(Measurement.station).all()

    # convert tuple to list
    # all_stations = [i for tup in all_stations for i in tup]
    all_stations = [list(tup[:4]) for tup in all_stations]

    return jsonify(all_stations)


@app.route('/api/v1.0/tobs')
def tobs():
    # Session = sqlalchemy.orm.sessionmaker(engine)

    # finds the last (most recent) date in the data
    with Session() as session:
        last_date = session.query(
            Measurement.date
        ).order_by(
            Measurement.date.desc()
        ).first()[0]

    # convert to date and subtract a year
    last_year = dt.datetime.strptime(
        last_date, '%Y-%m-%d'
    ) - dt.timedelta(days=365)

    most_active_station = engine.execute(
        'SELECT station '
        'FROM ('
        '       SELECT station, COUNT(station) AS mycount'
        '       FROM measurement '
        '       GROUP BY station '
        '       ORDER BY mycount DESC'
        '       ) '
        'measurement').first()[0]

    with Session() as session:
        temps = session.query(
            Measurement.date, Measurement.tobs, Measurement.prcp
        ).filter(
            Measurement.date > last_year,
            Measurement.station == most_active_station
        ).order_by(
            Measurement.date
        ).all()

    return_list = []

    for date, tobs, rain in temps:
        dict = {}
        dict['date'] = date
        dict['tobs'] = tobs
        dict['rain'] = rain

        return_list.append(dict)

    return jsonify(return_list)


@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def get_temp_data_dates(start, end=None):
    # Session = sqlalchemy.orm.sessionmaker(engine)

    if end is None:
        end = dt.date(2017, 8, 23)
    else:
        end = dt.datetime.strptime(end, '%Y-%m-%d').date()

    start = dt.datetime.strptime(start, '%Y-%m-%d').date()

    # start = start.date()
    # end = end.date()

    if start < dt.date(2010, 1, 1):
        start = dt.date(2010, 1, 1)

    if end > dt.date(2017, 8, 3):
        end = dt.date(2017, 8, 3)

    with Session() as session:
        mtobs = Measurement.tobs

        vals = session.query(
            func.min(mtobs), func.max(mtobs), func.avg(mtobs)
        ).filter(
            Measurement.date >= start,
            Measurement.date <= end
        ).all()

    out_info = {
        'start_date': start.strftime('%x'),
        'end_date': end.strftime('%x'),
        'min_temp': vals[0][0],
        'max_temp': vals[0][1],
        'avg_temp': round(vals[0][2], 1)
    }

    return jsonify(out_info)


if __name__ == '__main__':
    app.run(debug=True)
