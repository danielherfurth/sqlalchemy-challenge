# TODO uncomment line below before p2j.
# %matplotlib inline
from matplotlib import style

style.use('dark_background')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Reflect Tables into SQLAlchemy ORM
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)
conn = engine.connect()

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# View all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Exploratory Precipitation Analysis
# Find the most recent date in the data set.
first_date = session.query(
    Measurement.date
).order_by(
    Measurement.date
).first()

last_date = session.query(
    Measurement.date
).order_by(
    Measurement.date.desc()
).first()

last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')

# Design a query to retrieve the last 12 months of precipitation data and plot the results.
# Starting from the most recent data point in the database.
# Calculate the date one year from the last date in data set.
year_ago = last_date - dt.timedelta(days=365)

# Perform a query to retrieve the data and precipitation scores
precip = session.query(
    Measurement.date,
    Measurement.prcp
).filter(
    Measurement.date > year_ago
).order_by(Measurement.date).all()

# Save the query results as a Pandas DataFrame and set the index to the date column
# Sort the dataframe by date
precip_df = pd.DataFrame(
    precip,
    columns=['date', 'prcp']
).set_index('date').sort_index(ascending=True)

# Use Pandas Plotting with Matplotlib to plot the data

fig, ax = plt.subplots()
plt.rcParams.update({'font.size': 16})

precip_df.plot(
    figsize=(15, 12),
    title='Precipitation Data for August 2016 to August 2017',
    xlabel='Date',
    ylabel='Precipitation',
    fontsize=14,
    rot=45
)

plt.legend(['Precipitation'])
plt.tight_layout()

plt.savefig(r'Resources/precip.png', dpi=300)

# Use Pandas to calculate the summary statistics for the precipitation data
precip_df.describe()

# Exploratory Station Analysis
# Design a query to calculate the total number stations in the dataset

Stations = session.query(Station)
num_stations = Stations.count()

print(
    f'There are {num_stations} stations in this data.'
)

# Design a query to find the most active stations
# (i.e. what stations have the most rows?)
# List the stations and the counts in descending order.

active_stations = session.query(
    Measurement.station, func.count(Measurement.station)
).group_by(
    Measurement.station
).order_by(
    func.count(Measurement.station).desc()
).all()

for station, count in active_stations:
    print(f'Station {station} has {count} measurements.')

# Using the most active station id from the previous query,
# calculate the lowest, highest, and average temperature.
station = active_stations[0][0]

temps = session.query(
    Measurement.station, Measurement.date, Measurement.tobs
).filter(
    Measurement.station == station
).filter(
    Measurement.date > year_ago
).order_by(
    Measurement.date
).all()

temp_df = pd.DataFrame(
    temps,
    columns=['station', 'date', 'tobs']
)

low, high, mean = temp_df['tobs'].min(), temp_df['tobs'].max(), temp_df['tobs'].mean()

print(
    f'Low: {low}\n'
    f'High: {high}\n'
    f'Mean: {mean}'
)

# Using the most active station id
# Query the last 12 months of temperature observation data for this station
# and plot the results as a histogram

fig, ax = plt.subplots()

temp_df.plot(
    kind='hist',
    figsize=(15, 12),
    title='Observed Temperatures for August 2016 to August 2017',
    fontsize=16,
    width=2.3
)

plt.xlabel('Temperature')
plt.ylabel('Observations')
plt.legend(['Observed Temps'])

plt.tight_layout()
plt.savefig(r'Resources/temp_dist.png', dpi=300)

# Close Session
session.close()

