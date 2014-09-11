# trip_time_matrix.py

# Takes in a raw taxi data file, discretizes the latitude/longitude coordinates into a 
# grid at some scale, and returns (at present) the mean travel time between any two grid 
# elements. Can be extended to return quantile information as well. Should also 
# eventually write this data into a file to be stored somewhere.

# One problem: quantile information is not easily aggregated over different months. 
# Maybe there is a way to write a file for each "group" (corresponding to a trip
# between two grid elements in a given month---a lot of files) and then read in the
# files from different months corresponding to the same trip and then analyze them
# accordingly?

import numpy as np
import pandas as pd

# Read in raw data

taxi_data = pd.read_csv('../data/taxi_data_1.csv.gz',compression='gzip')

# Select relevant columns

taxi_data = taxi_data[['trip_time_in_secs', 'pickup_longitude', 'pickup_latitude', 
                        'dropoff_longitude', 'dropoff_latitude']]
                        
# Choose rounding tolerance for latitude/longitude coordinates. This determines the
# grid size. Number of decimal places must be at least the number of decimal places
# of tol

tol = .01

# Wastefully add columns of rounded lat/long coords that we will use to group our
# records. These rounded columns are stored as strings, because not doing so seems to
# cause rounding weirdness.

def roundCoord(coordinates, tol):
     return (np.rint(coordinates/tol)*tol).apply(lambda x: str(x)))
     
taxi_data['pick_lat_rnd'] = roundCoord(taxi_data['pickup_latitude'], tol)
taxi_data['pick_lon_rnd'] = roundCoord(taxi_data['pickup_longitude'], tol)
taxi_data['drop_lat_rnd'] = roundCoord(taxi_data['dropoff_latitude'], tol)
taxi_data['drop_lon_rnd'] = roundCoord(taxi_data['dropoff_longitude'], tol)

# Group trips by origin and destination. To access a particular group with rounded 
# coordinates, use the notation:
# trip_groups.get_group(('40.73', '-74.52', '40.71', '-73.99'))

trip_groups = taxi_data.groupby(['pick_lat_rnd','pick_lon_rnd',
                                    'drop_lat_rnd','drop_lon_rnd'])

# pickle

# Reservior sampling
