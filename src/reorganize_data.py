# reorganize_data.py

# To be run after data is merged using merge_taxi_data.py (if necessary).
# Imports taxi_data_*.csv.gz files, and reorganizes/pares down the data to what's 
# necessary for the project

import numpy as np
import pandas as pd
from datetime import datetime

# Read in data

taxi_data = pd.read_csv('../data/taxi_data_1.csv.gz',compression='gzip')

# Change times to pandas datetime format

taxi_data['pickup_datetime'] = pd.to_datetime(taxi_data['pickup_datetime'])
taxi_data['dropoff_datetime'] = pd.to_datetime(taxi_data['dropoff_datetime'])

# Sort by hack_license, then by pickup_datetime. Then reindex.

taxi_data.sort(['hack_license','pickup_datetime'], inplace = True)
taxi_data.index = range(len(taxi_data))

# Round lat/long coordinates with some tolerance tol

tol = .002

taxi_data['pickup_latitude'] = np.rint(taxi_data['pickup_latitude']/tol)*tol
taxi_data['pickup_longitude'] = np.rint(taxi_data['pickup_longitude']/tol)*tol
taxi_data['dropoff_latitude'] = np.rint(taxi_data['dropoff_latitude']/tol)*tol
taxi_data['dropoff_longitude'] = np.rint(taxi_data['dropoff_longitude']/tol)*tol

