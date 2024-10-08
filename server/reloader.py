import os
import threading
import warnings

from dataclasses import dataclass, asdict
import yaml
from watchfiles import watch

if "CONFIG" in os.environ:
    CONFIG_PATH = os.environ["CONFIG"]
else:
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')

@dataclass
class Config:
    TEAMS:dict[str, str]
    FLAG_FORMAT:str

    SYSTEM_TOKEN:str
    SYSTEM_PROTOCOL:str = None
    SYSTEM_URL:str = None
    SYSTEM_PORT:int = None
    SYSTEM_HOST: str = None  
    TEAM_TOKEN:str = None

    SUBMIT_FLAG_LIMIT: int
    SUBMIT_PERIOD: int
    FLAG_LIFETIME: int

    SERVER_PASSWORD:str

    ENABLE_API_AUTH:bool
    API_TOKEN:str 

@dataclass
class Config_manager(Config):
    is_initialized = False
    def __init__(self):
        self._load()
        self.observer_thread = threading.Thread(target=self.watch_for_changes, daemon=True)
        self.observer_thread.start()
        self.is_initialized = True
        
    def watch_for_changes(self):
        for _ in watch(CONFIG_PATH):
            print('hot reloading config...')
            self._load()

    def _load(self):
        with open(CONFIG_PATH, 'r') as config_file:
            self.raw_config = yaml.safe_load(config_file)
        print('new config loaded')
    
    # def __setattr__(self, name: str, value: None) -> None:
    #     if name in Config.__dataclass_fields__ and self.is_initialized:
    #         self.save()
    #     return super().__setattr__(name, value)
    
    def raw_write(self, config:dict):
        with open(CONFIG_PATH, 'w') as config_file:
            yaml.dump(config, config_file)

    def save(self):
        self.raw_write(self.raw_config)

    @property
    def raw_config(self):
        """access the config as a dict"""
        return {k:v for k, v in asdict(self).items() if k in Config.__dataclass_fields__}
    
    def validate_config(self, config:dict):
        for key in config.keys():
            if not key in Config.__dataclass_fields__:
                raise Exception(f'key {key} not found')
        
        for key in Config.__dataclass_fields__:
            if not key in config:
                warnings.warn(f'additional key {key} found in new config')    

    @raw_config.setter
    def raw_config(self, value:dict):
        self.validate_config(value)
        if self.is_initialized:
            value = self.raw_config | value
        super().__init__(**value)

config = Config_manager()