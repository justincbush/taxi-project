# reorganize_data.py

# To be run after data is merged using merge_taxi_data.py (if necessary).
# Imports taxi_data_*.csv.gz files, and reorganizes/pares down the data to what's 
# necessary for the project

import numpy as np
import pandas as pd
from datetime import datetime

# Read in data

taxi_data = pd.read_csv('../data/taxi_data_1.csv.gz',compression='gzip')

# Select columns we care about

taxi_data = taxi_data[['hack_license','pickup_datetime','dropoff_datetime',
                        'trip_distance', 'pickup_longitude', 'pickup_latitude', 
                        'dropoff_longitude', 'dropoff_latitude', 'tip_amount',
                        'total_amount']]

# Change times to pandas datetime format

taxi_data['pickup_datetime'] = pd.to_datetime(taxi_data['pickup_datetime'])
taxi_data['dropoff_datetime'] = pd.to_datetime(taxi_data['dropoff_datetime'])

# Sort by hack_license, then by pickup_datetime. Then reindex.

taxi_data.sort(['hack_license','pickup_datetime'], inplace = True)
taxi_data.index = range(len(taxi_data))

# Round lat/long coordinates with some tolerance tol

tol = .002

taxi_data['pick_lat_rnd'] = np.round(np.rint(taxi_data['pickup_latitude']/tol)*tol,3)
taxi_data['pick_lon_rnd'] = np.round(np.rint(taxi_data['pickup_longitude']/tol)*tol,3)
taxi_data['drop_lat_rnd'] = np.round(np.rint(taxi_data['dropoff_latitude']/tol)*tol,3)
taxi_data['drop_lon_rnd'] = np.round(np.rint(taxi_data['dropoff_longitude']/tol)*tol,3)

# Groupby on two levels using (pick_lat_rnd, pick_lon_rnd) as the first level and
# (drop_lat_rnd, drop_lon_rnd) as the second. May require multiindexing.

# Try multiindexing

orig = list(zip(taxi_data['pick_lat_rnd'],taxi_data['pick_lon_rnd']))
dest = list(zip(taxi_data['drop_lat_rnd'],taxi_data['drop_lon_rnd']))

taxi_data.groupby(['pick_lat_rnd','pick_lon_rnd'])



# Plot a histogram of trip times betweeen 

