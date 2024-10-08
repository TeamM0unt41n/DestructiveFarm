import re
import time
from datetime import datetime

from flask import jsonify, render_template, request
from pymongo import DESCENDING, MongoClient

from server import app, auth, database, reloader
from server.models import FlagStatus
from server.reloader import config
from os import environ

PASSWORD = environ.get("MONGO_ROOT_PASSWORD", "password")

client = MongoClient(host="novara-mongo", port=27017, username="root", password=PASSWORD)
db = client.get_database("db")

@app.template_filter('timestamp_to_datetime')
def timestamp_to_datetime(s):
    return datetime.fromtimestamp(s)


@app.route('/')
@auth.auth_required
def index():
    distinct_values = {}

    for column in ['sploit', 'status', 'team']:
        distinct_values[column] = db.flags.distinct(column)

    server_tz_name = time.strftime('%Z')
    if server_tz_name.startswith('+'):
        server_tz_name = 'UTC' + server_tz_name

    return render_template('index.html',
                           flag_format=config.FLAG_FORMAT,
                           distinct_values=distinct_values,
                           server_tz_name=server_tz_name)


FORM_DATETIME_FORMAT = '%Y-%m-%d %H:%M'
FLAGS_PER_PAGE = 30


@app.route('/ui/show_flags', methods=['POST'])
@auth.auth_required
def show_flags():    
    query = {}

    # Filter by sploit, status, and team
    for column in ['sploit', 'status', 'team']:
        value = request.form[column]
        if value:
            query[column] = value

    # Filter by flag and checksystem_response (using case-insensitive search)
    for column in ['flag', 'checksystem_response']:
        value = request.form[column]
        if value:
            query[column] = {'$regex': value.lower(), '$options': 'i'}

    # Time-based filtering
    for param in ['time-since', 'time-until']:
        value = request.form[param].strip()
        if value:
            timestamp = round(datetime.strptime(value, FORM_DATETIME_FORMAT).timestamp())
            if param == 'time-since':
                query['time'] = {'$gte': timestamp}
            elif param == 'time-until':
                query['time'] = {'$lte': timestamp}

    # Pagination
    page_number = int(request.form['page-number'])
    if page_number < 1:
        raise ValueError('Invalid page-number')

    skip = FLAGS_PER_PAGE * (page_number - 1)
    
    # Retrieve flags with pagination and sorting by time (descending)
    flags = list(db.flags.find(query).sort('time', DESCENDING).skip(skip).limit(FLAGS_PER_PAGE))

    # Get total count for pagination
    total_count = db.flags.count_documents(query)

    return jsonify({
        'rows': [dict(item) for item in flags],
        'rows_per_page': FLAGS_PER_PAGE,
        'total_count': total_count,
    })


@app.route('/ui/post_flags_manual', methods=['POST'])
@auth.auth_required
def post_flags_manual():    
    # Extract flags from the provided text
    flags = re.findall(config.FLAG_FORMAT, request.form['text'])

    cur_time = round(time.time())
    rows = [{
        'flag': item,
        'sploit': 'Manual',
        'team': '*',
        'time': cur_time,
        'status': FlagStatus.QUEUED.name
    } for item in flags]

    # Use bulk operations to insert flags, ignoring duplicates
    operations = [
        {'updateOne': {
            'filter': {'flag': row['flag']},
            'update': {'$setOnInsert': row},
            'upsert': True
        }} for row in rows
    ]

    if operations:
        db.flags.bulk_write(operations)

    return ''
