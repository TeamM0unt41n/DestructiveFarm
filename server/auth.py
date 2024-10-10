from fastapi import Request, HTTPException
from fastapi.responses import Response

from server.config import config

def authenticate():
    return Response(
        'Could not verify your access level for that URL. '
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def api_auth(request: Request):
    if config.ENABLE_API_AUTH:
        if request.headers.get('X-Token', '') != config.API_TOKEN:
            raise HTTPException(403, 'Provided token is invalid.')