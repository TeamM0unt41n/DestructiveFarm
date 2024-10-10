import re
import time

from datetime import datetime
from pymongo import DESCENDING, UpdateOne
from typing import Annotated, Optional

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from server.models import Flag_Status
from server.config import config
from server.database import db

tempates = Jinja2Templates('templates')

view_router = APIRouter()

def timestamp_to_datetime(s):
    return datetime.fromtimestamp(s)

@view_router.get('/')
def index(request:Request):
    distinct_values = {}

    for column in ['sploit', 'status', 'team']:
        distinct_values[column] = db.flags.distinct(column)

    server_tz_name = time.strftime('%Z')
    if server_tz_name.startswith('+'):
        server_tz_name = 'UTC' + server_tz_name

    return tempates.TemplateResponse(request=request, name='index.html',
                                     context={'flag_format':config.FLAG_FORMAT,
                                              'distinct_values':distinct_values,
                                              'server_tz_name':server_tz_name})


FORM_DATETIME_FORMAT_MIN = '%Y-%m-%d %H:%M'
FORM_DATETIME_FORMAT_SEC = '%Y-%m-%d %H:%M:%S'

@view_router.post('/ui/show_flags')
async def show_flags(
        request:Request,
        page_number:Optional[Annotated[int, Form()]] = None, 
        time_since:Optional[Annotated[str, Form()]] = None, 
        time_until:Optional[Annotated[str, Form()]] = None, 
        checksystem_response:Optional[Annotated[str, Form()]] = None, 
        flag:Optional[Annotated[str, Form()]] = None, 
        team:Optional[Annotated[str, Form()]] = None, 
        status:Optional[Annotated[str, Form()]] = None, 
        sploit:Optional[Annotated[str, Form()]] = None, 
        flags_per_page:int = 30
        ):    
    query = {}

    form_data = await request.form()

    # Filter by sploit, status, and team
    for column in ['sploit', 'status', 'team']:
        value = form_data[column]
        if value:
            query[column] = value

    # Filter by flag and checksystem_response (using case-insensitive search)
    for column in ['flag', 'checksystem_response']:
        value = form_data[column]
        if value:
            query[column] = {'$regex': value.lower(), '$options': 'i'}

    # Time-based filtering
    for param in ['time-since', 'time-until']:
        value = form_data[param].strip()
        if value:
            try:
                timestamp = round(datetime.strptime(value, FORM_DATETIME_FORMAT_MIN).timestamp())
            except ValueError as e:
                try:
                    timestamp = round(datetime.strptime(value, FORM_DATETIME_FORMAT_SEC).timestamp())
                except ValueError:
                    raise HTTPException(400, f'invalide time: {e.args}')
            if param == 'time-since':
                query['time'] = {'$gte': timestamp}
            elif param == 'time-until':
                query['time'] = {'$lte': timestamp}

    # Pagination
    page_number = int(form_data['page-number'])
    if page_number < 1:
        raise ValueError('Invalid page-number')

    skip = flags_per_page * (page_number - 1)
    
    # Retrieve flags with pagination and sorting by time (descending)
    flags = list(db.flags.find(query, {'_id':False}).sort('time', DESCENDING).skip(skip).limit(flags_per_page))

    # Get total count for pagination
    total_count = db.flags.count_documents(query)

    return JSONResponse({
        'rows': [dict(item) for item in flags],
        'rows_per_page': flags_per_page,
        'total_count': total_count,
    })


@view_router.post('/ui/post_flags_manual')
def post_flags_manual(text:Annotated[str, Form()]):    
    # Extract flags from the provided text
    flags = re.findall(config.FLAG_FORMAT, text)

    cur_time = round(time.time())
    rows = [{
        'flag': item,
        'sploit': 'Manual',
        'team': '*',
        'time': cur_time,
        'status': Flag_Status.QUEUED.name,
        'checksystem_response':None
    } for item in flags]

    # Use bulk operations to insert flags, ignoring duplicates
    operations = [
        UpdateOne(
            {'flag': row['flag']},
            {'$setOnInsert': row},
            upsert=True
        ) for row in rows
    ]

    if operations:
        db.flags.bulk_write(operations)

    return ''
