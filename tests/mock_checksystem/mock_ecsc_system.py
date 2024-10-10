from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from random import choice, randint
from secrets import token_hex, token_urlsafe
import re

class Flag_Model(BaseModel):
    flag:str

api = FastAPI()


@api.put('/submit/')
async def submit_flag(flags:list[str]):
    result = []
    for flag in flags:
        verdict = choice(['valide', 'queue', 'invalide']) if re.match(r'[A-Z0-9]{31}=', flag) is not None else 'invalide'
        match verdict:
            case 'valide':
                result.append({'msg':f"[{flag}] [{verdict}] {choice(['accepted', 'congrat'])}", 'flag':flag})
                break

            case 'queue':
                result.append({'msg': f"[{flag}] [{verdict}] {choice(['timeout', 'game not started', 'retry later', 'game over', 'is not active yet', 'is not up', 'no such flag'])}", 'flag':flag})
                break

            case 'invalide':
                result.append({'msg': f"[{flag}] [{verdict}] {choice(['bad', 'wrong', 'expired', 'denied', 'unknown', 'your own', 'flag already claimed', 'too old', 'not in database', 'already submitted', 'invalid flag'])}", 'flag':flag})
                break

    return JSONResponse(result)

@api.get('/retreive/')
def get_flag():
    result =''
    for i in range(randint(1, 10)):
        result += f'{token_hex(16)[:31].upper()}='
        result += token_urlsafe(randint(10, 40))
    
    return result