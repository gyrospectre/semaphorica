# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from datetime import datetime


class BaseModel(object):

    def __init__(self, **kwargs):
        self.param_defaults = {}

    def __str__(self):
        return json.dumps(self.AsDict(), ensure_ascii=True, sort_keys=True)

    def AsDict(self):
        data = {}

        for (key, value) in self.param_defaults.items():
            if isinstance(getattr(self, key, None), (list, tuple, set)):
                data[key] = list()
                for subobj in getattr(self, key, None):
                    if getattr(subobj, 'AsDict', None):
                        data[key].append(subobj.AsDict())
                    else:
                        data[key].append(subobj)

            elif getattr(getattr(self, key, None), 'AsDict', None):
                data[key] = getattr(self, key).AsDict()

            elif getattr(self, key, None):
                data[key] = getattr(self, key, None)

        return data

class Message(BaseModel):

    """A class representing a single message to be routed. """

    def __init__(self, **kwargs):
        self.param_defaults = {
            'created': None,
            'id': None,
            'received': datetime.utcnow().isoformat(),
            'source_module': None,
            'source_identity': None,
            'body': None,
            'provenance': [],
            'tlp': "TLP:AMBER"  # Safe default to Amber, should be overwritten by module
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return json.dumps(self.AsDict(), ensure_ascii=True, sort_keys=True)