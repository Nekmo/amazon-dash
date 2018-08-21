"""Amazon Dash.
"""

import logging
import click
import sys

import os
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


def latest_release(package):
    if sys.version_info > (3,):
        from xmlrpc import client
    else:
        import xmlrpclib as client
    pypi = client.ServerProxy('https://pypi.python.org/pypi')
    available = pypi.package_releases(package)
    if not available:
        # Try to capitalize pkg name
        available = pypi.package_releases(package.capitalize())

    if not available:
        return
    return available[0]


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    import amazon_dash
    from amazon_dash import __version__
    latest = latest_release('amazon-dash')
    release = ('This is the latest release' if latest == __version__
               else 'There is a new version available: {}. Upgrade it using: '
                    'sudo pip install -U amazon-dash'.format(latest))
    click.echo('You are running Amazon-dash v{} using Python {}.\n{}\n'
               'Installation path: {}\n'
               'Current path: {}\n'.format(
        __version__, sys.version.split()[0], release, os.path.dirname(amazon_dash.__file__), os.getcwd()
    ))
    ctx.exit()


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
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
def cli(loglevel):
    from amazon_dash import __version__
    click.secho('Welcome to Amazon-dash v{} using Python {}'.format(__version__, sys.version.split()[0]),
                fg='cyan')
    create_logger('amazon-dash', loglevel)


@cli.command(help='Run server')
@click.option('--config', type=click.Path(), help='Path to config file.', default=CONFIG_FILE)
@click.option('--root-allowed', is_flag=True, default=False,
              help='Allow execute commands on config file as root.')
@click.option('--ignore-perms', is_flag=True, default=False,
              help='Do not check the permissions of the configuration file. '
                   'Use this option at your own risk in secure environments (like Docker).')
def run(config, root_allowed, ignore_perms):
    click.secho('Listening for events. Amazon-dash will execute the events associated with '
               'the registered buttons.', fg='yellow')
    from amazon_dash.listener import Listener
    Listener(config, ignore_perms).run(root_allowed=root_allowed)


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
@click.option('--interface', help='Network interface.', default=None)
def discovery(interface):
    from amazon_dash.discovery import discover
    discover(interface)
