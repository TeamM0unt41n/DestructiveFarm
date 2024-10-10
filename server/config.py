import os
import threading
import yaml
from watchfiles import watch
from typing import Union
from server.models import Config_Model

if "CONFIG" in os.environ:
    CONFIG_PATH = os.environ["CONFIG"]
else:
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')

class ConfigManager(Config_Model):
    is_initialized: bool = False

    def __init__(self):
        super().__init__(**self._load())
        threading.Thread(target=self.watch_for_changes, daemon=True).start()
        self.is_initialized = True

    def watch_for_changes(self):
        for _ in watch(CONFIG_PATH):
            print('Hot reloading config...')
            self.raw_config = self._load()

    def _load(self):
        with open(CONFIG_PATH, 'r') as config_file:
            data = yaml.safe_load(config_file)
        print('New config loaded')
        return data
    
    def raw_write(self, config: dict):
        with open(CONFIG_PATH, 'w') as config_file:
            yaml.dump(config, config_file)

    def save(self):
        self.raw_write(self.model_dump())

    @property
    def raw_config(self):
        """Access the config as a dict"""
        return self.model_dump()

    @raw_config.setter
    def raw_config(self, value: Union[dict, Config_Model]):
        if isinstance(value, Config_Model):
            value = value.model_dump()

        if self.is_initialized:
            value = {**self.model_dump(), **value}

        super().__init__(**value)

config = ConfigManager()