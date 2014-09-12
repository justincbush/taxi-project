# trip_to_sql.py

# Takes taxi data, cleans it, forms a data frame with percentile information about
# trip times between different locations, and exports it as a sql file.

import numpy as np
import pandas as pd

# Read in raw data

sample_size = 10000

taxi_data = pd.read_csv('../data/taxi_data_1.csv.gz',compression='gzip',nrows=sample_size)

# Select relevant columns

taxi_data = taxi_data[['trip_time_in_secs', 'pickup_longitude', 'pickup_latitude', 
                        'dropoff_longitude', 'dropoff_latitude']]
                        
# Remove rows with blatantly wrong coordinates

min_lat = 40.5
max_lat = 40.9
min_lon = -74.3
max_lon = -73.7

good_pickup_lat = (taxi_data['pickup_latitude']>min_lat) \
                        & (taxi_data['pickup_latitude']<max_lat)
good_dropoff_lat = (taxi_data['dropoff_latitude']>min_lat) \
                        & (taxi_data['dropoff_latitude']<max_lat)
good_pickup_lon = (taxi_data['pickup_longitude']>min_lon) \
                        & (taxi_data['pickup_longitude']<max_lon)
good_dropoff_lon = (taxi_data['dropoff_longitude']>min_lon) \
                        & (taxi_data['dropoff_longitude']<max_lon)                       
                        
taxi_data = taxi_data[good_pickup_lat&good_dropoff_lat&good_pickup_lon&good_dropoff_lon]
                        
# Choose rounding tolerance for latitude/longitude coordinates. This determines the
# grid size.

tol = .01

# Wastefully add columns of rounded lat/long coords that we will use to group our
# records. These rounded columns are stored as strings, because not doing so seems to
# cause rounding weirdness.

def roundCoord(coordinates, tol):
     return (np.rint(coordinates/tol)*tol).apply(lambda x: str(x))
     
taxi_data['pick_lat_rnd'] = roundCoord(taxi_data['pickup_latitude'], tol)
taxi_data['pick_lon_rnd'] = roundCoord(taxi_data['pickup_longitude'], tol)
taxi_data['drop_lat_rnd'] = roundCoord(taxi_data['dropoff_latitude'], tol)
taxi_data['drop_lon_rnd'] = roundCoord(taxi_data['dropoff_longitude'], tol)

# Group trips by origin and destination. To access a particular group with rounded 
# coordinates, use the notation:
# trip_groups.get_group(('40.73', '-74.52', '40.71', '-73.99'))

trip_groups = taxi_data.groupby(['pick_lat_rnd','pick_lon_rnd',
                                    'drop_lat_rnd','drop_lon_rnd'],sort=False)
                                    
# Filter by some minimum number of trips for adequate statistics.

min_num_trips = 2

trip_groups_thresh = trip_groups.filter(lambda x: len(x) >= min_num_trips).groupby(
            ['pick_lat_rnd','pick_lon_rnd','drop_lat_rnd','drop_lon_rnd'],sort=False)

# list of desired percentiles

percentiles = [10, 25, 50, 75, 90]

# dictionary to be supplied to agg method. Thanks to Isaac for the double lambdas

dict_of_funcs = {'count': lambda x: len(x)}
for pct in [10,50,90]:
    dict_of_funcs['percentile' + str(pct)] = \
        (lambda p: (lambda x: np.percentile(x,p)))(pct)
    

    
sql_data = trip_groups_thresh['trip_time_in_secs'].agg(dict_of_funcs)




