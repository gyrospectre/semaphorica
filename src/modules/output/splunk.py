import json
import os

from classes import BaseOutputModule

from models import Message

class Splunk(BaseOutputModule):

    def __init__(self, credentials=None):

        if credentials is None:
            token = os.getenv('SPLUNK_TOKEN')
        else:
            token = credentials.get('token')

        self._name = self.__class__.__name__.lower()
        self._token = token

    def send(self, cfg, messages):
        postdata = {}
        index = cfg.get('index')
        sourcetype = cfg.get('sourcetype')

        if index is not None:
            postdata['index'] = index

        if sourcetype is not None:
            postdata['sourcetype'] = sourcetype

        postdata['event'] = json.loads(str(messages))
        print(json.dumps(postdata))
        #curl -k "https://mysplunkserver.example.com:8088/services/collector" \
        #    -H "Authorization: Splunk CF179AE4-3C99-45F5-A7CC-3284AA91CF67" \
        #    -d '{"event": "Hello, world!", "sourcetype": "manual"}'

    @classmethod
    def validate_cfg(cls, cfg):
        valid, msg = BaseOutputModule.validate_cfg(cfg)

        if not valid:
            return valid, msg

        if cfg.get('host') is None:
            return False, "Parameter 'host' must be provided."

        return True, 'Configuration validated successfully.'
