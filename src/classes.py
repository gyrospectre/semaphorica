import json

from abc import ABC
from abc import abstractmethod


class BaseModule(ABC):
    pass

class BaseInputModule(BaseModule):
    @abstractmethod
    def fetch(self, key, checkpoint):
        pass

    @classmethod
    def validate_cfg(cls, cfg):

        missing_keys = []
        required_keys = []

        for key in required_keys:
            if key not in cfg:
                missing_keys.append(key)

        if missing_keys:
            return False, 'Invalid config. Missing keys: {} for {}'.format(
                ', '.join(missing_keys), json.dumps(cfg, indent=2)
            )

        return True, 'Configuration valid.'

class BaseOutputModule(BaseModule):
    @abstractmethod
    def send(self, key):
        pass

    @classmethod
    def validate_cfg(cls, cfg):

        missing_keys = []
        required_keys = []

        for key in required_keys:
            if key not in cfg:
                missing_keys.append(key)

        if missing_keys:
            return False, 'Invalid config. Missing keys: {} for {}'.format(
                ', '.join(missing_keys), json.dumps(cfg, indent=2)
            )

        return True, 'Configuration valid.'

class BaseProcessModule(BaseModule):
    @abstractmethod
    def process(self, key):
        pass
