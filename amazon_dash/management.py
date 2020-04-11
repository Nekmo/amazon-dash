"""Amazon Dash.
"""

import logging
import click
import sys

import os
from click_default_group import DefaultGroup

from amazon_dash.audio import WavAudio

CONFIG_FILE = 'amazon-dash.yml'

BRICKED_MESSAGE = """\
December 31 is the last day to block requests from your Amazon-dash buttons to Amazon servers. \
In 2020 your buttons can be bricked in an update from Amazon servers.\
"""


directory = os.path.dirname(os.path.abspath(__file__))


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


def blue_light_confirm(no_input):
    if no_input:
        click.secho('Used --no-input, ignoring confirm...')
    else:
        click.confirm('Is the blue light flashing?', abort=True)


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
    click.secho(BRICKED_MESSAGE, fg='magenta')
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


@cli.command(help='Set up a device\'s Wi-Fi network')
@click.option('--ssid', type=str, prompt='SSID (Wireless network name)')
@click.option('--password', prompt='Network password', hide_input=True,
              help='Password of the wifi network to configure on the device')
@click.option('--no-enable-wifi', is_flag=True)
@click.option('--no-input', is_flag=True)
def configure(ssid, password, no_enable_wifi, no_input):
    click.echo('This command allows you to configure the Wi-Fi network of an amazon-dash device.')
    click.secho('After the configuration, you must block the Internet connection of the device '
                'before using it.', fg='red')
    click.secho('Not blocking Internet connections after setting it could brick your device.', fg='red', blink=True)
    click.secho('Hold the button on your Amazon dash device for 5 seconds until '
                'the light blinks blue.', fg='blue')
    blue_light_confirm(no_input)
    from amazon_dash.wifi import ConfigureAmazonDash, enable_wifi
    if not no_enable_wifi:
        enable_wifi()
    configure = ConfigureAmazonDash()
    info = configure.get_info()
    click.echo('Device info:')
    click.echo('\n'.join(['{}: {}'.format(key.replace('_', ' ').title(), value)
                          for key, value in info.items()]))
    click.echo('Configuring...')
    configure.configure(ssid, password)
    click.echo('Success! The button is already configured. However, before using it, '
               'you must block the Internet connections of the device.')
    click.secho('Not blocking Internet connections could brick your device.', fg='red', blink=True)


@cli.command('hack-device', help='Hack an amazon-dash device that has never been connected to amazon servers.')
@click.option('--no-input', is_flag=True)
@click.option('--loop', type= int, default=5)
def hack_device(no_input, loop):
    click.echo('This command allows you to hack a Amazon-dash device built on May 2016 and earlier. '
               'Even if your device was purchased later, it is likely that it has an older firmware installed. ')
    click.echo('You only need to use this command if you have never connected your device to Amazon servers in '
               'the past.')
    click.echo('Sound is used to hack the device (Amazon Dash buttons include a microphone). It is recommended to '
               'use earbuds near the button. Remember to turn up the volume on your computer.')
    click.secho('To start the hack, place the earbuds and hold the button on your Amazon dash device for 5 seconds '
                'until the light blinks blue. Observe the led during the hack.', fg='blue')
    blue_light_confirm(no_input)
    wav_file = os.path.join(directory, 'hack.wav')
    WavAudio(wav_file).loop_play(loop)
    click.echo('What happened to the led during the hack?')
    click.echo('* The LED turns green: the exploit worked! Run the amazon-dash "configure" command')
    click.echo('* The LED turns off: the device is probably patched. If you have previously connected '
               'your device to amazon servers maybe you can run the amazon-dash "configure" command')
