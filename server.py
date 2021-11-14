
from datetime import datetime
import csv
import json
import sqlite3
from flask import Flask, request, g
from flask_cors import CORS, cross_origin
from io import StringIO

# import enum
# from typing import NamedTuple

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

### Database setup

DATABASE = './database.db'

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

        db.row_factory = make_dicts
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    '''The database initialization function that is meant to be called once.'''
    with app.app_context():
        db = get_db()
        with app.open_resource('./schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

### Database helper

def query_db(query, args=()):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return rv


def query_db_single(query, args=()):
    rv = query_db(query, args=args)
    return (rv[0] if rv else None)

### Database operation

def add_sensor_geo(geo_data):
    if not geo_data.keys() & {'id', 'lat', 'lon'}:
        return geo_data
    _id = str(geo_data['id'])
    lat = geo_data['lat']
    lon = geo_data['lon']

    # insert or update if device by id already exist
    # query_db("INSERT INTO device (id, lon, lat) VALUES(?, ?, ?) ON DUPLICATE KEY UPDATE id=VALUES(id), lon=VALUES(lon), lat=VALUES(lat)", [_id, lon, lat])
    # query_db("REPLACE INTO device (id, lon, lat) VALUES(?, ?, ?)", [_id, lon, lat])
    data = query_device_geo(_id)
    if data is None:
        query = 'INSERT INTO device(id, lon, lat) VALUES("%s", ?, ?)' % _id
        res = query_db(query, [lon, lat])
    else:
        print("updating")
        res = query_db("UPDATE device SET lon=?, lat=? WHERE id=?", [lon, lat, _id])

    get_db().commit()
    # insert into device(id, lon,lat) values(1, 53, -1)

    print(geo_data)
    return "<p>registered sensor {0} at geo, {1}</p>".format(_id, res)

def add_sensor_log(entry):
    if not entry.keys() & {'id'}:
        return entry

    print(entry)
    # datetime.now().timestamp,
    # time = entry['time'] if 'time' in entry else str(datetime.now())
    time = str(datetime.now())
    query_db("insert into log (id, time) values (?,?)", [ entry["id"],
                 time
                ])

    get_db().commit()
    return "<p>added log</p>"

def query_all_geo():
    return query_db("SELECT * FROM device")

def query_all_log():
    return query_db("SELECT * FROM log")

def query_device_geo(the_id):
    return query_db_single("select * from device where id = ?", [the_id])

def query_device_log(the_id):
    return query_db("select * from log where id = ?", [the_id])

### App routes

@app.route('/')
def index():
    return 'Hello TDOMers'

@app.route("/log", methods=["POST"])
def logPostHandler():
    '''Log csv data from the sensor'''
    if len(request.data) == 0:
        return "Malformated query request"

    try:
        print(request.data)
        log_json = request.data
        log_data = json.loads(log_json)
    except ValueError as _:
        return "Malformated json request"
    # scsv = request.data
    # f = StringIO(scsv)
    # reader = csv.reader(f, delimiter=',')
    # entries = list(csv_reader)
    return add_sensor_log(log_data)

@app.route("/geo", methods=["POST"])
def geoPostHandler():
    '''Add geographical data (json) from the app'''
    # print("recv", request.data)
    if len(request.data) == 0:
        return "Malformated query request"

    try:
        geo_json = request.data
        geo_data = json.loads(geo_json)
    except ValueError as _:
        return "Malformated json request"

    return add_sensor_geo(geo_data)

def queryHandler(query_type, dId=None):
    if query_type == 'geo':
        if dId is not None:
            return query_device_geo(dId)
        else:
            return query_all_geo()

    elif query_type == 'log':
        if dId is not None:
            return query_device_log(dId)
        else:
            return query_all_log()
    else:
        return "require type in ['geo', 'log']"

@cross_origin()
@app.route("/get", methods=["GET"])
def getHandler():
    args = request.args

    query_type = args.get('type', type=str)
    dId = args.get('id', type=str)
    results = queryHandler(query_type, dId=dId)
    return {"response": results}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
