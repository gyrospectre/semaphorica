import json

from classes import BaseOutputModule

from datetime import datetime

from models import Message

class File(BaseOutputModule):

    def send(self, cfg, messages):
        if cfg.get('clobber') == True:
            mode = "w"
        else:
            mode = "a"

        filename = cfg.get('filename')

        if '{$NOW}' in filename:
            filename=filename.replace('{$NOW}', datetime.utcnow().isoformat("T","seconds"))

        with open(filename, mode) as outfile:
            for message in messages:
                outfile.write(str(message))

    @classmethod
    def validate_cfg(cls, cfg):
        valid, msg = BaseOutputModule.validate_cfg(cfg)

        if not valid:
            return valid, msg

        if cfg.get('filename') is None:
            return False, "Unsupported action, only 'filename' is supported."

        return True, 'Configuration validated successfully.'
