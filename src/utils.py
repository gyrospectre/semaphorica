import boto3
import inspect
import logging
import sys
import yaml

from botocore.exceptions import ClientError

from classes import BaseModule

from importlib import import_module

from pythonjsonlogger import jsonlogger


SUPPORTED_CP_PROVIDERS = ['aws-ssm']

def setup_logging(log_level):
    logger = logging.getLogger()

    logger.setLevel(log_level)

    handler = logging.StreamHandler()

    handler.setFormatter(
        jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(levelname)s %(lambda)s %(message)s'
        )
    )

    logger.addHandler(handler)

    stdouthandler = logging.StreamHandler(sys.stdout)
    logger.addHandler(stdouthandler)

    logger.removeHandler(logger.handlers[0])


def get_logger():
    logger = logging.getLogger()
    
    return logger

def load_route(filename):
    with open(filename, "r") as stream:
        return yaml.safe_load(stream)

def load_module(modulename, type):
    try:
        module = import_module(f'modules.{type}.{modulename.lower()}')

        mods = []
        for _, obj in inspect.getmembers(module):
            if (inspect.isclass(obj)
                and issubclass(obj, BaseModule) and not _.startswith('Base')):
                mods.append(obj)

        if len(mods) == 0:
            raise AttributeError(f'No classes extending base modules in {modulename}!')

        if len(mods) > 1:
            raise AttributeError(f'Multiple classes extending base modules in {modulename}!')

        return mods[0]

    except (ModuleNotFoundError, AttributeError) as e:
        raise Exception(f'Module for "{modulename}" is not available: {e}')

def load_aws_ssm(key):
    ssm = boto3.client('ssm')
    try:
        parameter = ssm.get_parameter(Name=key, WithDecryption=True)
    except ClientError as e:
        return None, None

    return parameter['Parameter']['Value'], parameter['Parameter']['Version']

def save_aws_ssm(key, value):
    ssm = boto3.client('ssm')

    oldvalue, oldversion = load_aws_ssm(key)
    if oldvalue == value:
        # No change required
        return True

    resp = ssm.put_parameter(
        Name=key,
        Description='Checkpoint for Semaphorica',
        Value=str(value),
        Type='String',
        DataType='text',
        Overwrite=True
    )
    if resp['Version'] != oldversion:
        return True
    else:
        raise Exception(f"'AWS SSM Parameter '{key}' could not be updated!")

def load_checkpoint(route, provider):
    if provider not in SUPPORTED_CP_PROVIDERS:
        raise Exception('Invalid checkpoint provider!')
    
    if provider == 'aws-ssm':
        value, version = load_aws_ssm(f'/semaphorica/{route}')
        if value is not None:
            #return int(value)
            return None
        else:
            return None

def save_checkpoint(route, provider, value):
    if provider not in SUPPORTED_CP_PROVIDERS:
        raise Exception('Invalid checkpoint provider!')
    
    if provider == 'aws-ssm':
        return save_aws_ssm(f'/semaphorica/{route}', value)
