import logging
import os
import utils

from classes import BaseModule

from importlib import import_module

ROUTE_DIR = '/cfg'
DEFAULT_CKPT_PROVIDER = 'aws-ssm'
LOGGER = utils.get_logger()

utils.setup_logging(logging.INFO)


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
    input = utils.load_module(module,'input')()
 
    checkpoint = utils.load_checkpoint(route=name, provider=chkpt_provider)
    LOGGER.debug(f'Successfully loaded checkpoint - {checkpoint}.')

    messagelist, lastid = input.fetch(config, checkpoint)
    if messagelist is None:
        LOGGER.info('No new messages, route complete.')
        return
 
    LOGGER.info(f'Received {len(messagelist)} messages.')

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

def run_routes():
    for entry in os.scandir(os.getcwd()+ROUTE_DIR):
        if entry.path.endswith(".yaml") and entry.is_file():
            route_config = utils.load_route(entry.path)
            routename = next(iter(route_config))
            routecfg = route_config[routename]

            try:
                validate_cfg(routecfg)
                LOGGER.info(f"Running '{next(iter(route_config))}' route.")
                run_single_route(routename, routecfg)

            except Exception as e:
                LOGGER.error(f'Error running {routename}, skipping! Error: {e}')

if __name__ == "__main__":
    run_routes()