import requests
import json

from classes import BaseInputModule
from datetime import datetime
from models import Message


SUPPORTED_DATA_TYPES = {
    # Exit List: https://metrics.torproject.org/collector.html#type-tordnsel
    'exit-addresses': 'https://check.torproject.org/exit-addresses'
}


class TorProject(BaseInputModule):

    def __init__(self, credentials=None):

        self._urls = SUPPORTED_DATA_TYPES
        self._name = self.__class__.__name__.lower()

    def parse(self, results):
        nodelist = []

        rawnode = []
        for result in results.splitlines():
            if result.startswith('ExitNode'):
                # New node, save previous if it exists
                if rawnode != []:
                    node = {}
                    node['ExitAddresses'] = []
                    for element in rawnode:
                        parts = element.split()
                        if parts[0] == 'ExitNode':
                            node['Fingerprint'] = parts[1]
                        elif parts[0] == 'ExitAddress':
                            node['ExitAddresses'].append(parts[1])
                        elif parts[0] == 'Published':
                            node['Published'] = datetime.strptime(' '.join(parts[1:]), '%Y-%m-%d %H:%M:%S').isoformat()
                        elif parts[0] == 'LastStatus':
                            node['LastStatus'] = datetime.strptime(' '.join(parts[1:]), '%Y-%m-%d %H:%M:%S').isoformat()

                    nodelist.append(node)         

                rawnode = [result]

            else:
                rawnode.append(result)

        return nodelist

    def fetch(self, cfg, checkpoint=None):
        dataType = cfg.get('type') 
        r = requests.get(self._urls[dataType])
        r.raise_for_status()

        results = r.text

        if len(results.splitlines()) == 0:
            # Nothing new
            return None, None

        nodelist = self.parse(results)

        messagelist = []
        for node in nodelist:
            message = Message(
                source_module=self._name,
                id=node['Fingerprint'],
                body=json.dumps(node, default=str),
                source_identity=f'{self._name}_{dataType}',
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

        if cfg.get('type') is None:
            return False, "No data type provided."

        if cfg.get('type') not in ['exit-addresses']:
            return False, "Invalid data type. Only 'exit-addresses' is supported."

        return True, 'Configuration validated successfully.'
