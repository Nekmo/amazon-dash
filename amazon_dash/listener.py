import time
from collections import defaultdict

import threading

from amazon_dash.config import Config
from amazon_dash.confirmations import get_confirmation
from amazon_dash.exceptions import InvalidConfig, InvalidDevice
from amazon_dash.execute import logger, ExecuteCmd, ExecuteUrl, ExecuteHomeAssistant, ExecuteOpenHab, ExecuteIFTTT
from amazon_dash.scan import scan_devices

DEFAULT_DELAY = 10
"""
On seconds. By default, 10 seconds. Minimum time that must pass between pulsations of the Amazon Dash button.
"""

EXECUTE_CLS = {
    'cmd': ExecuteCmd,
    'url': ExecuteUrl,
    'homeassistant': ExecuteHomeAssistant,
    'openhab': ExecuteOpenHab,
    'ifttt': ExecuteIFTTT,
}
"""
Execute classes registered.
"""

last_execution = defaultdict(lambda: 0)
"""
Last time a device was executed. Value on unix time.
"""


class Device(object):
    """Set the execution method for the device
    """
    execute_instance = None  #: Execute cls instance

    def __init__(self, src, data=None, config=None):
        """

        :param str src: Mac address
        :param data: device data
        """
        data = data or {}
        config = config or {}

        if isinstance(src, Device):
            src = src.src
        self.src = src.lower()
        self.data = data
        execs = [cls(self.name, data) for name, cls in EXECUTE_CLS.items() if name in self.data]
        if len(execs) > 1:
            raise InvalidConfig(
                extra_body='There can only be one method of execution on a device. The device is {}. '.format(self.name)
            )
        elif len(execs):
            self.execute_instance = execs[0]
            self.execute_instance.validate()
        self.confirmation = get_confirmation(src, data, config.get('confirmations', {}))

    @property
    def name(self):
        """Name on self.data or mac address

        :return: name
        :rtype: str
        """
        return self.data.get('name', self.src)

    def execute(self, root_allowed=False):
        """Execute this device

        :param bool root_allowed: Only used for ExecuteCmd
        :return: None
        """
        logger.debug('%s device executed (mac %s)', self.name, self.src)
        if not self.execute_instance:
            msg = '%s: There is not execution method in device conf.'
            logger.warning(msg, self.name)
            self.send_confirmation(msg % self.name, False)
            return
        try:
            result = self.execute_instance.execute(root_allowed)
        except Exception as e:
            self.send_confirmation('Error executing the device {}: {}'.format(self.name, e), False)
            raise
        else:
            result = 'The {} device has been started and is running right now'.format(self.name) \
                if result is None else result
            result = result or 'The {} device has been executed successfully'.format(self.name)
            self.send_confirmation(result)
        return result

    def send_confirmation(self, message, success=True):
        """Send success or error message to configured confirmation

        :param str message: Body message to send
        :param bool success: Device executed successfully to personalize message
        :return: None
        """
        message = message.strip()
        if not self.confirmation:
            return
        try:
            self.confirmation.send(message, success)
        except Exception as e:
            logger.warning('Error sending confirmation on device {}: {}'.format(self.name, e))


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
    if not device in config['devices']:
        raise InvalidDevice('Device {} is not in config file.'.format(device))
    logger.info(Device(device, config['devices'][device], config).execute(root_allowed))
