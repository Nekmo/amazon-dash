from collections import defaultdict
import time
import logging

from amazon_dash.config import Config
from amazon_dash.scan import scan, print_pkt


DEFAULT_DELAY = 10

last_execution = defaultdict(lambda: 0)
logger = logging.getLogger('amazon-dash')


class Device(object):
    def __init__(self, device, data=None):
        self.src = getattr(device, 'src', device).lower()
        self.data = data

    @property
    def name(self):
        return self.data.get('name', self.src)

    def execute(self):
        logger.debug('%s device executed (mac %s)', self.name, self.src)
        if not 'cmd' in self.data:
            logger.warning('%s: There is no cmd in device conf.', self.name)


class Listener(object):
    def __init__(self, config_path):
        self.config = Config(config_path)
        self.settings = self.config.get('settings', {})
        self.devices = {key.lower(): Device(key, value) for key, value in self.config['devices'].items()}
        assert len(self.devices) == len(self.config['devices']), "Duplicate(s) MAC(s) on devices config."

    def on_push(self, device):
        src = device.src.lower()
        if last_execution[src] + self.settings.get('delay', DEFAULT_DELAY) > time.time():
            return
        last_execution[src] = time.time()
        self.execute(device)

    def execute(self, device):
        src = device.src.lower()
        device = self.devices[src]
        device.execute()

    def run(self):
        scan(self.on_push, lambda d: d.src.lower() in self.devices)
