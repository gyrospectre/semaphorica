import logging
import os
import sys
import time
import utils

from classes import BaseModule

from importlib import import_module

ROUTE_DIR = '/cfg'
DEFAULT_CKPT_PROVIDER = 'aws-ssm'

LOGGER = utils.get_logger()

def _default_response(status, module, exectime, results=None):
    response = {}
    response[module] = {}

    response[module]['status'] = status
    response[module]['exectime'] = exectime

    if results is not None:
        response[module]['results'] = results

    return response

def _fail(module, exectime):
    return _default_response('fail', module=module, exectime=exectime)

def _success(module, results, exectime):
    return _default_response('success', module=module, exectime=exectime, results=str(results))

def validate_cfg(config):
    inputmod = next(iter(config['input']))
    input = utils.load_module(inputmod,'input')
    valid, message = input.validate_cfg(config['input'][inputmod])

    if not valid:
        raise Exception(f'Invalid config for {inputmod}! {message}')

    for outputcfg in config['outputs']:
        outputmod = next(iter(outputcfg))
        output = utils.load_module(outputmod,'output')

        valid, message = output.validate_cfg(outputcfg[outputmod])

        if not valid:
            raise Exception(f'Invalid config for {outputmod}! {message}')

def run_input(name, module, config, chkpt_provider):
    checkpoint = None
    input = utils.load_module(module,'input')()
 
    if chkpt_provider != 'none':
        checkpoint = utils.load_checkpoint(route=name, provider=chkpt_provider)
        LOGGER.debug(f'Successfully loaded checkpoint - {checkpoint}.')

    messagelist, lastid = input.fetch(config, checkpoint)
    if messagelist is None:
        LOGGER.info('No new messages, route complete.')
        return
 
    LOGGER.info(f'Received {len(messagelist)} messages.')

    if chkpt_provider != 'none':
        save_result = utils.save_checkpoint(
            route=name,
            provider=chkpt_provider,
            value=lastid
        )
        if save_result:
            LOGGER.debug(f'Checkpoint updated successfully - {lastid}.')
    
    return messagelist

def run_output(name, module, config, messages):
    output = utils.load_module(module,'output')()
    output.send(config, messages)
    LOGGER.info(f'Sent {len(messages)} messages to {module}.')

def run_single_route(name, cfg):
    inputmod = next(iter(cfg['input']))
    messages = run_input(
        name=name,
        module=inputmod,
        config=cfg['input'][inputmod],
        chkpt_provider=cfg.get('checkpoint_provider', DEFAULT_CKPT_PROVIDER)
    )
    if messages is not None:
        for output in cfg['outputs']:
            outputmod = next(iter(output))
            run_output(
                name=name,
                module=outputmod,
                config=output[outputmod],
                messages=messages
            )
    return len(messages)

def run_routes(runModules=None):
    results = []

    for entry in os.scandir(os.getcwd()+ROUTE_DIR):

        filename = os.path.basename(entry.path)
        if runModules == None or os.path.splitext(filename)[0] in runModules:

            if entry.path.endswith(".yaml") and entry.is_file():
                route_config = utils.load_route(entry.path)
                routename = next(iter(route_config))
                routecfg = route_config[routename]
                starttime = time.time()

                try:
                    validate_cfg(routecfg)

                    if not routecfg.get('disabled'):
                        LOGGER.info(f"Running '{next(iter(route_config))}' route.")
                        numResults = run_single_route(routename, routecfg)
                        results.append(_success(module=routename, results=numResults, exectime=time.time()-starttime))
                    else:
                        LOGGER.info(f"Skipping '{next(iter(route_config))}' route, set to disabled.")

                except Exception as e:
                    LOGGER.error(f'Error running {routename}, skipping! Error: {e}')
                    results.append(_fail(module=routename, exectime=time.time()-starttime))

    return results

if __name__ == "__main__":
    utils.setup_logging(logging.INFO)

    if sys.argv[1:] == []: 
        modules = None
    else:
        modules = sys.argv[1:]

    run_routes(modules)
