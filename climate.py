# %%
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
# %%
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

# %%

# Design a query to retrieve the last 12 months of precipitation data and plot the results.
# Starting from the most recent data point in the database.
year_ago = last_date - dt.timedelta(days=365)

# Calculate the date one year from the last date in data set.
year_ago

# Perform a query to retrieve the data and precipitation scores
precip = session.query(
    Measurement.date,
    Measurement.prcp
).filter(
    Measurement.date > year_ago
).order_by(Measurement.date).all()

# %%
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
    title='Precipitation Data for 2016-8-24 to 2017-8-23',
    xlabel='Date',
    ylabel='Precipitation',
    fontsize=14,
    rot=45
)

plt.legend(['Precipitation'])
plt.tight_layout()

plt.savefig(r'Resources/precip.png', dpi=300)
# %%

# Use Pandas to calcualte the summary statistics for the precipitation data


# %% md

# Exploratory Station Analysis

# %%

# Design a query to calculate the total number stations in the dataset


# %%

# Design a query to find the most active stations (i.e. what stations have the most rows?)
# List the stations and the counts in descending order.


# %%

# Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.


# %%

# Using the most active station id
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram


# %% md

# Close session

# %%

# Close Session
session.close()

# %%
