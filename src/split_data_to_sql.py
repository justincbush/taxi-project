# split_data_to_sql.py

# Reads files generated by split_by_day_hour.py, groups the data by lat/long of origin and
# destination, computes the percentiles for travel times for each group, and then outputs
# the result into a single SQLite database.

import numpy as np
import pandas as pd
import sqlite3 as db
import os

for filename in os.listdir('../data/dayhour'):
    path = '../data/dayhour/' + str(filename)
    print 'Loading '+filename    
    taxi_data = pd.read_csv(path, header=None, names=['index','medallion','hack_license', 
                            'vendor_id', 'rate_code', 'store_and_fwd_flag',
                            'pickup_datetime', 'dropoff_datetime', 'passenger_count',
                            'trip_time_in_secs', 'trip_distance', 'pickup_longitude',
                            'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude',
                            'payment_type', 'fare_amount', 'surcharge', 'mta_tax',
                            'tip_amount', 'tolls_amount', 'total_amount','day_of_week',
                            'hour'])

    # select relevent columns

    taxi_data = taxi_data[['trip_time_in_secs', 'pickup_longitude', 'pickup_latitude', 
                        'dropoff_longitude', 'dropoff_latitude', 'day_of_week', 'hour']]
                        
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

    # Round lat/long coords that we will use to group our
    # records. These rounded columns are stored as strings, because not doing so seems to
    # cause rounding weirdness.

    def roundCoord(coordinates, tol):
         return (np.rint(coordinates/tol)*tol).apply(lambda x: str(x))
     
    taxi_data['pickup_latitude'] = roundCoord(taxi_data['pickup_latitude'], tol)
    taxi_data['pickup_longitude'] = roundCoord(taxi_data['pickup_longitude'], tol)
    taxi_data['dropoff_latitude'] = roundCoord(taxi_data['dropoff_latitude'], tol)
    taxi_data['dropoff_longitude'] = roundCoord(taxi_data['dropoff_longitude'], tol)

                                    
    # taxi_data = taxi_data['trip_time_in_secs', 'pickup_latitude', 'pickup_longitude', \
    #			'dropoff_latitude', 'dropoff_longitude', 'day_of_week', 'hour']

    # Group trips by origin and destination. To access a particular group with rounded 
    # coordinates, use the notation:
    # trip_groups.get_group(('40.73', '-74.52', '40.71', '-73.99'))

    trip_groups = taxi_data.groupby(['pickup_latitude','pickup_longitude','dropoff_latitude',
                                        'dropoff_longitude','day_of_week','hour'],sort=False)
 
    # Filter by some minimum number of trips for adequate statistics.

    min_num_trips = 10

    trip_groups_thresh = trip_groups.filter(lambda x: len(x) >= min_num_trips).groupby(
                ['pickup_latitude','pickup_longitude','dropoff_latitude','dropoff_longitude',
                 'day_of_week','hour'],sort=False)

    # list of desired percentiles

    percentiles = [10, 25, 50, 75, 90]

    # dictionary to be supplied to agg method. Thanks to Isaac for the double lambdas

    dict_of_funcs = {'count': lambda x: len(x)}
    for pct in percentiles:
        dict_of_funcs['percentile' + str(pct)] = \
            (lambda p: (lambda x: np.percentile(x,p)))(pct)
    
    sql_data = trip_groups_thresh['trip_time_in_secs'].agg(dict_of_funcs)

    # Write to sql database

    con = db.connect('full_taxi_data.db' )

    sql_data.to_sql('test_table',con, if_exists='append')

    con.commit()
    con.close()
