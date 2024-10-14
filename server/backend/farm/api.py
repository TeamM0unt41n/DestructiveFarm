import requests

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from farm import auth
from farm.config import config
from farm.spam import is_spam_flag
from farm.models import Flag_Status, Flag_Model, Config_Model
from farm.database import db

from json import JSONDecodeError

from pymongo import UpdateOne
from pymongo.errors import BulkWriteError
from time import time

client_router = APIRouter(prefix='/api', dependencies=[Depends(auth.api_auth)])

@client_router.get('/get_config')
def get_config():
    print(config.TEAMS)
    filtered_config = {key: value for key, value in config.raw_config.items() if key in ['TEAMS', 'TOKEN', 'FLAG_FORMAT', 'FLAG_LIFETIME', 'SUBMIT_PERIOD']}
    if config.USE_ADVANCED_STRATEGIES:
        try:
            r = requests.get(config.STRATEGY_ENDPOINT)
            if r.ok:
                teams_to_attack = r.json()
                filtered_config['TEAMS'] = {team_id:team_ip for team_id, team_ip in config.TEAMS.items() if team_id in teams_to_attack}
        except (JSONDecodeError, requests.exceptions.InvalidSchema):
            print('failed parsing json, falling back to attacking all teams')
        else:
            print('Failed requesting teams from strategy endpoint, falling back to attack all teams.')
    return JSONResponse(filtered_config)

@client_router.post('/post_flags')
def post_flags(flags:list[Flag_Model]):
    flags = filter(lambda item: not is_spam_flag(item.flag), flags)

    cur_time = round(time())

    operations = [
        UpdateOne(
            {'flag': item.flag},  # Filter based on 'flag'
            {
                '$setOnInsert': {
                    'flag': item.flag,
                    'sploit': item.sploit,
                    'team': item.team,
                    'time': cur_time,
                    'status': Flag_Status.QUEUED.name,
                    'checksystem_response': None
                }
            },
            upsert=True  # Perform upsert (insert if not exists, ignore if exists)
        )
        for item in flags
    ]

    try:
        db.flags.bulk_write(operations)
    except BulkWriteError as e:
        print(f"Bulk write error: {e.details}")


@client_router.post('/api/set_config')
def request_config_reload(new_config:Config_Model):
    config.raw_config = new_config
    config.save()