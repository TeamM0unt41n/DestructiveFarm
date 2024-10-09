from collections import namedtuple
from enum import Enum
from pydantic import BaseModel
from typing import Optional 


class Flag_Status(Enum):
    QUEUED = 0
    SKIPPED = 1
    ACCEPTED = 2
    REJECTED = 3

class Config_Model(BaseModel):
    TEAMS: dict[str, str]
    FLAG_FORMAT: str
    SYSTEM_TOKEN: str
    SYSTEM_PROTOCOL: Optional[str] = None
    SYSTEM_URL: Optional[str] = None
    SYSTEM_PORT: Optional[int] = None
    SYSTEM_HOST: Optional[str] = None  
    TEAM_TOKEN: Optional[str] = None
    SUBMIT_FLAG_LIMIT: int
    SUBMIT_PERIOD: int
    FLAG_LIFETIME: int
    SERVER_PASSWORD: str
    ENABLE_API_AUTH: bool
    API_TOKEN: str

Flag = namedtuple('Flag', ['flag', 'sploit', 'team', 'time', 'status', 'checksystem_response'])
SubmitResult = namedtuple('SubmitResult', ['flag', 'status', 'checksystem_response'])

class Flag_Model(BaseModel):
    flag:str
    sploit:str
    team:str