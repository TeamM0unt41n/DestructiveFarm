import time

from flask import request, jsonify

from server import app, auth, database, reloader
from server.reloader import config
from server.models import FlagStatus
from server.spam import is_spam_flag

from pymongo import UpdateOne, MongoClient
from pymongo.errors import BulkWriteError
from time import time
from os import environ


PASSWORD = environ.get("MONGO_ROOT_PASSWORD", "password")

client = MongoClient(host="novara-mongo", port=27017, username="root", password=PASSWORD)
db = client.get_database("db")

@app.route('/api/get_config')
@auth.api_auth_required
def get_config():
    return jsonify({key: value for key, value in config.raw_config if key not in ['PASSWORD', 'TOKEN']})

@app.route('/api/post_flags', methods=['POST'])
@auth.api_auth_required
def post_flags():
    # Get JSON data from request
    flags = request.get_json()

    # Filter out spam flags
    flags = [item for item in flags if not is_spam_flag(item['flag'])]

    # Get current time
    cur_time = round(time())

    # Create a list of upsert operations to insert or ignore duplicates
    operations = [
        UpdateOne(
            {'flag': item['flag']},  # Filter based on 'flag'
            {
                '$setOnInsert': {
                    'flag': item['flag'],
                    'sploit': item['sploit'],
                    'team': item['team'],
                    'time': cur_time,
                    'status': FlagStatus.QUEUED.name
                }
            },
            upsert=True  # Perform upsert (insert if not exists, ignore if exists)
        )
        for item in flags
    ]

    try:
        # Perform bulk upsert
        db.flags.bulk_write(operations)
    except BulkWriteError as e:
        # Log the error or handle it appropriately
        print(f"Bulk write error: {e.details}")

    return ''


@app.route('/api/set_config', methods=['POST'])
@auth.api_auth_required
def request_config_reload():
    config._load()
    return ''