import json

from abc import ABC
from abc import abstractmethod


TLP_2_0_LABELS = ['TLP:RED', 'TLP:AMBER', 'TLP:AMBER+STRICT', 'TLP:GREEN', 'TLP:CLEAR']


class BaseModule(ABC):
    pass

class BaseInputModule(BaseModule):
    @abstractmethod
    def fetch(self, key, checkpoint):
        pass

    @classmethod
    def validate_cfg(cls, cfg):

        missing_keys = []
        required_keys = ['tlp']

        for key in required_keys:
            if key not in cfg:
                missing_keys.append(key)

        if missing_keys:
            return False, 'Invalid config. Missing keys: "{}" for {}'.format(
                ', '.join(missing_keys), json.dumps(cfg, indent=2)
            )

        if cfg.get('tlp') not in TLP_2_0_LABELS:
            return False, f'Invalid TLP label. Must be one of {TLP_2_0_LABELS}. See https://www.first.org/tlp/'

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
