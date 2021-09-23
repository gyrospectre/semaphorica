import os

from classes import BaseOutputModule

from models import Message

class File(BaseOutputModule):

    def send(self, cfg, messages):
        with open(cfg['filename'], "a") as outfile:
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
