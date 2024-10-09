import time

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from server import auth
from server.reloader import config
from server.spam import is_spam_flag
from server.models import Flag_Status, Flag_Model, Config_Model
from server.database import db

from pymongo import UpdateOne
from pymongo.errors import BulkWriteError
from time import time

client_router = APIRouter('/api', dependencies=[Depends(auth.api_auth)])

@client_router.get('/get_config')
def get_config():
    return JSONResponse({key: value for key, value in config.raw_config if key not in ['PASSWORD', 'TOKEN']})

@client_router.post('/post_flags')
def post_flags(flags:list[Flag_Model]):
    flags = filter(flags, lambda item: is_spam_flag(item.flag))

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
                    'status': Flag_Status.QUEUED.name
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


@client_router.route('/api/set_config', methods=['POST'])
def request_config_reload(new_config:Config_Model):
    config.raw_config = new_config