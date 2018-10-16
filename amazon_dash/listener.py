import time
from collections import defaultdict

import threading

from amazon_dash.config import Config
from amazon_dash.device import Device
from amazon_dash.exceptions import InvalidDevice
from amazon_dash.execute import logger
from amazon_dash.scan import scan_devices

DEFAULT_DELAY = 10
"""
On seconds. By default, 10 seconds. Minimum time that must pass between pulsations of the Amazon Dash button.
"""

"""
Execute classes registered.
"""

last_execution = defaultdict(lambda: 0)
"""
Last time a device was executed. Value on unix time.
"""


class Listener(object):
    """Start listener daemon for execute on button press
    """

    root_allowed = False  #: Only used for ExecuteCmd

    def __init__(self, config_path, ignore_perms=False):
        """

        :param str config_path: Path to config file
        """
        self.config = Config(config_path, ignore_perms)
        self.settings = self.config.get('settings', {})
        self.devices = {key.lower(): Device(key, value, self.config)
                                     for key, value in self.config['devices'].items()}
        assert len(self.devices) == len(self.config['devices']), "Duplicate(s) MAC(s) on devices config."

    def on_push(self, device):
        """Press button. Check DEFAULT_DELAY.

        :param scapy.packet.Packet device: Scapy packet
        :return: None
        """
        src = device.src.lower()
        if last_execution[src] + self.settings.get('delay', DEFAULT_DELAY) > time.time():
            return
        last_execution[src] = time.time()
        self.execute(device)

    def execute(self, device):
        """Execute a device. Used if the time between executions is greater than DEFAULT_DELAY

        :param scapy.packet.Packet device: Scapy packet
        :return: None
        """
        src = device.src.lower()
        device = self.devices[src]
        threading.Thread(target=device.execute, kwargs={
            'root_allowed': self.root_allowed
        }).start()

    def run(self, root_allowed=False):
        """Start daemon mode

        :param bool root_allowed: Only used for ExecuteCmd
        :return: loop
        """
        self.root_allowed = root_allowed
        scan_devices(self.on_push, lambda d: d.src.lower() in self.devices, self.settings.get('interface'))


def test_device(device, file, root_allowed=False):
    """Test the execution of a device without pressing the associated button

    :param str device: mac address
    :param str file: config file
    :param bool root_allowed: only used for ExecuteCmd
    :return: None
    """
    config = Config(file)
    config.read()
    if not device in config.devices:
        raise InvalidDevice('Device {} is not in config file.'.format(device))
    logger.info(config.devices[device].execute(root_allowed))
