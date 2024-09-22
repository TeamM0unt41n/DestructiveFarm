import time

from flask import request, jsonify

from server import app, auth, database, reloader
from server.models import FlagStatus
from server.spam import is_spam_flag

import requests


@app.route('/api/get_config')
@auth.api_auth_required
def get_config():
    config:dict[str, dict] = reloader.get_config()
    if strategy_endpoint := config.get('STRATEGY_ENDPOINT', None):
        r = requests.get(strategy_endpoint)
        if r.ok:
            teams_to_attack = r.json()['teams']
            config['TEAMS'] = {name:ip for name, ip in config['TEAMS'].items() if name in teams_to_attack}
        else:
            print(f'Error requesting strategy endpoint: {r.text}')
    return jsonify({key: value for key, value in config.items()
                    if 'PASSWORD' not in key and 'TOKEN' not in key})


@app.route('/api/post_flags', methods=['POST'])
@auth.api_auth_required
def post_flags():
    flags = request.get_json()
    flags = [item for item in flags if not is_spam_flag(item['flag'])]

    cur_time = round(time.time())
    rows = [(item['flag'], item['sploit'], item['team'], cur_time, FlagStatus.QUEUED.name)
            for item in flags]

    db = database.get()
    db.executemany("INSERT OR IGNORE INTO flags (flag, sploit, team, time, status) "
                   "VALUES (?, ?, ?, ?, ?)", rows)
    db.commit()

    return ''
