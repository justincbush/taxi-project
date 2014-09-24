# taxi_website.py

# Flask application for displaying taxi project data on a website.

# Outside imports

from flask import Flask, render_template, request, redirect, json, g, send_file  
import urllib
import sqlite3 as sql
import numpy as np
import matplotlib
matplotlib.use("Agg")           # prevents python rocketship
import matplotlib.pyplot as plt
import StringIO

# import local modules

import google_api as api
import taxi_database as dbase
import figures

# Databases

trip_times_database = 'trip_times_data.db'
trip_speeds_database = 'trip_speeds_data.db'
trip_fares_database = 'trip_fares_data.db'

# path = '/Users/jcb/Documents/Data Incubator/taxi-project/src/website/'
# trip_times_database = path + 'trip_times_data.db'
# trip_speeds_database = path + 'databases/trip_speeds_data.db'
# trip_fares_database = path + 'databases/trip_fares_data.db'

databases = {'times': trip_times_database, 'speeds': trip_speeds_database,
                'fares': trip_fares_database}
tol = .01 # Rounding tolerance that generated these databases

# Beginning of app

app = Flask(__name__)

@app.route('/')
def test_site():
    return render_template('test_site.html')
    
@app.route('/output', methods = ['POST'])
def record_data():
    start_point = request.form.get('start_point')
    end_point = request.form.get('end_point')
    day = int(request.form.get('day'))
    hour = int(request.form.get('hour'))
    ampm = request.form.get('ampm')
    if ampm == 'pm':
        hour += 12
    days_of_week = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday',
                5: 'Saturday', 6: 'Sunday'}
    day_name = days_of_week[day]
        
    start_coords = api.get_lat_lon_coords(start_point)
    end_coords = api.get_lat_lon_coords(end_point)
    distance = api.get_trip_distance(','.join(str(i) for i in start_coords),
                                     ','.join(str(j) for j in end_coords))
                                     
    def roundCoord(coordinates, tol=tol):
        return str((np.rint(coordinates/tol)*tol))
    
    output = {}
    for database in databases:
        output[database] = \
            dbase.query_database_row(databases[database],
                                     start_lat_rnd=roundCoord(start_coords[0]),
                                     start_lon_rnd=roundCoord(start_coords[1]),
                                     end_lat_rnd=roundCoord(end_coords[0]),
                                     end_lon_rnd=roundCoord(end_coords[1]),
                                     day=day, hour=hour)        

    
    samples = output['times'][6]
    quantiles = [[num/60.0 for num in sorted(output['times'][7:12])],
                 sorted([distance/spd for spd in output['speeds'][7:12]])]
    print 'Quantiles:',quantiles
    quantiles_to_url = \
        'z'.join(str(num) for list in quantiles for num in list)
    
    labels = ['old method','new method']
    labels_to_url = \
        ','.join(label.replace(' ','+') for label in labels)
        
    map_url = api.make_static_map_url(start_point,end_point,size='500x400',
                        maptype='terrain', markers=start_point+'|'+end_point)
    
    return render_template('output.html', map_url=map_url, quantiles=quantiles_to_url,
                                labels = labels_to_url,
                                text_time=str(hour)+':00', samples=str(samples), 
                                day_name=days_of_week[day])

@app.route('/fig-<quantiles>-<labels>')
def make_figure(quantiles,labels):

    split_data = np.array([float(num) for num in quantiles.split('z')])

    quantiles_list = [split_data[:5],split_data[5:]]
    
    quantile_labels = [label.replace('+',' ') for label in labels.split(',')]
    
    fig = figures.multi_boxplot(quantiles_list,quantile_labels)
    
    img = StringIO.StringIO()
    fig.savefig(img)        #  bbox_inches='tight' ?
    img.seek(0)
    return send_file(img, mimetype='image/png')
    
    

if __name__ == '__main__':
    app.run(debug=True)