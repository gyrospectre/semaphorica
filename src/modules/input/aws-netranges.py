import requests
import json

from classes import BaseInputModule
from datetime import datetime
from models import Message


URL = "https://ip-ranges.amazonaws.com/ip-ranges.json"


class AWSNetRanges(BaseInputModule):

    def __init__(self, credentials=None):

        self._url = URL
        self._name = self.__class__.__name__.lower()

    def fetch(self, cfg, checkpoint=None):
        r = requests.get(self._url)
        r.raise_for_status()

        results = json.loads(r.text)

        if len(results['prefixes']) == 0:
            # Nothing new
            return None, None

        messagelist = []
        for prefix in results['prefixes']:
            prefix['createDate'] = datetime.strptime(results['createDate'], '%Y-%m-%d-%H-%M-%S').isoformat()
            message = Message(
                source_module=self._name,
                body=json.dumps(prefix, default=str),
                source_identity=self._name,
                provenance=[self._name],
                tlp=cfg.get('tlp'),
            )
            messagelist.append(message)

        return messagelist, None

    @classmethod
    def validate_cfg(cls, cfg):
        valid, msg = BaseInputModule.validate_cfg(cfg)

        if not valid:
            return valid, msg

        return True, 'Configuration validated successfully.'
