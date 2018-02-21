"""Amazon Dash.
"""

import logging
import click
import sys
from click_default_group import DefaultGroup

CONFIG_FILE = 'amazon-dash.yml'


def create_logger(name, level=logging.INFO):
    """Create a Logger and set handler and formatter

    :param name: logger name
    :param level: logging level
    :return: None
    """
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-7s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)


@click.group(cls=DefaultGroup, default='run', default_if_no_args=True)
@click.option('--info', 'loglevel', help='set logging to info', default=True,
              flag_value=logging.INFO)
@click.option('--warning', 'loglevel', help='set logging to warning',
              flag_value=logging.WARNING)
@click.option('--quiet', 'loglevel', help='set logging to ERROR',
              flag_value=logging.ERROR)
@click.option('--debug', 'loglevel', help='set logging to DEBUG',
              flag_value=logging.DEBUG)
@click.option('--verbose', 'loglevel', help='set logging to COMM',
              flag_value=5)
def cli(loglevel):
    from amazon_dash import __version__
    click.echo('Welcome to Amazon-dash v{} using Python {}'.format(__version__, sys.version.split()[0]))
    create_logger('amazon-dash', loglevel)


@cli.command(help='Run server')
@click.option('--config', type=click.Path(), help='Path to config file.', default=CONFIG_FILE)
@click.option('--root-allowed', is_flag=True, default=False,
              help='Allow execute commands on config file as root')
def run(config, root_allowed):
    click.echo('Listening for events. Amazon-dash will execute the events associated with '
               'the registered buttons.')
    from amazon_dash.listener import Listener
    Listener(config).run(root_allowed=root_allowed)


@cli.command('check-config', help='Validate the configuration file.')
@click.option('--config', type=click.Path(), help='Path to config file.', default=CONFIG_FILE)
def check_config(config):
    from amazon_dash.config import check_config
    check_config(config)


@cli.command('test-device', help='Test a configured device without press button.')
@click.argument('device', type=str)
@click.option('--config', type=click.Path(), help='Path to config file.', default=CONFIG_FILE)
@click.option('--root-allowed', is_flag=True, default=False,
              help='Allow execute commands on config file as root')
def test_device(device, config, root_allowed):
    from amazon_dash.listener import test_device
    test_device(device, config, root_allowed)


@cli.command(help='Discover Amazon Dash device on network.')
def discovery():
    from amazon_dash.discovery import discover
    discover()
