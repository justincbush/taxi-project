from flask import Flask, render_template, request, redirect
import numpy as np
import urllib
import json
import sqlite3 as sql

# Tolerance and rounding function to translate raw lat/lon data into our grids

tol = .01
def roundCoord(coordinates, tol):
     return str((np.rint(coordinates/tol)*tol))
     
# Beginning of app

app = Flask(__name__)

@app.route('/')
def hello_world():
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
        
    start_format = start_point.replace(' ','+')
    end_format = end_point.replace(' ','+')
    
    url_prefix = 'https://maps.googleapis.com/maps/api/geocode/json?address='
    start_link = url_prefix + start_format
    end_link = url_prefix + end_format
    
    start_query = urllib.urlopen(start_link)
    end_query = urllib.urlopen(end_link)
    
    start_data = json.loads(start_query.read())
    end_data = json.loads(end_query.read())
    
    start_lat = start_data['results'][0]['geometry']['location']['lat']
    start_lon = start_data['results'][0]['geometry']['location']['lng']
    end_lat = end_data['results'][0]['geometry']['location']['lat']
    end_lon = end_data['results'][0]['geometry']['location']['lng']
    
    # Round coordinates and convert to strings
        
    start_lat = roundCoord(start_lat, tol)
    start_lon = roundCoord(start_lon, tol)
    end_lat = roundCoord(end_lat, tol)
    end_lon = roundCoord(end_lon, tol)
    
    conn = sql.connect('taxi_data.db')
    
    
    return redirect('/')
    
if __name__ == '__main__':
    app.run()