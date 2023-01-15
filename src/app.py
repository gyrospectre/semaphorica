import logging
import utils
import semaphorica

utils.setup_logging(logging.INFO)
LOGGER = utils.get_logger()


def lambda_handler(event, context):

    trigger = event.get('trigger', 'daily')

    run_for_modules = event.get('modules', None)
    debug_mode = event.get('debug', False)

    if debug_mode:
        LOGGER.setLevel(logging.DEBUG)
        logging.getLogger('boto3').setLevel(logging.INFO)
        logging.getLogger('botocore').setLevel(logging.INFO)

    LOGGER.info(
        'Kicking off Semaphorica for the {} run. Sources: {}'.format(
            trigger.upper(),
            ', '.join(run_for_modules) if run_for_modules else 'ALL'
        )
    )

    resp = semaphorica.run_routes(runModules=run_for_modules)

    LOGGER.info(
        {
            'message': 'Finished execution of Semaphorica for the {} run. '
            'Sources: {}'.format(
                trigger.upper(),
                ', '.join(run_for_modules) if run_for_modules else 'ALL'
            ),
            'results': resp
        }
    )

    return 