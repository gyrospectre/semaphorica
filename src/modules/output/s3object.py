import boto3

from classes import BaseOutputModule

from datetime import datetime

from models import Message


SESSION = boto3.Session()


class S3Object(BaseOutputModule):

    def send(self, cfg, messages):
        s3 = SESSION.resource(
            's3',
            region_name=cfg.get('region')
        )

        objectname = cfg.get('object_name')

        if '{$NOW}' in objectname:
            objectname=objectname.replace('{$NOW}', datetime.utcnow().isoformat("T","seconds"))

        s3.Object(
            bucket_name=cfg.get('bucket_name'),
            key=objectname,
        ).put(
            Body=str(messages),
        )

    @classmethod
    def validate_cfg(cls, cfg):
        valid, msg = BaseOutputModule.validate_cfg(cfg)

        if not valid:
            return valid, msg
        required_keys = ['object_name', 'bucket_name', 'region']

        for key in required_keys:
            if cfg.get(key) is None:
                return False, f"Required value '{key}' missing."

        return True, 'Configuration validated successfully.'
